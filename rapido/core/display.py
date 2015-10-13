from zope.interface import implements

from .interfaces import IDisplay
from .exceptions import NotAllowed, NotFound


class Display:
    implements(IDisplay)

    def __init__(self, context):
        self.context = context
        self.app = self.context

    def _parse_path(self, path):
        directive = path[1]
        obj_id = path[2]
        if len(path) > 3:
            action = path[3]
        else:
            action = 'view'
        return (directive, obj_id, action)

    def GET(self, path, request):
        (directive, obj_id, action) = self._parse_path(path)
        result = ""
        redirect = ""
        if directive == "form":
            form = self.app.get_form(obj_id)
            if not form:
                raise NotFound(obj_id)
            result = form.display(edit=True)
        elif directive == "document":
            doc = self.app.get_document(obj_id)
            if not doc:
                raise NotFound(obj_id)
            editmode = (action == "edit")
            result = doc.display(edit=editmode)
        else:
            raise NotAllowed()
        return (result, redirect)

    def POST(self, path, request):
        (directive, obj_id, action) = self._parse_path(path)
        result = ""
        redirect = ""
        if directive == "form":
            form = self.app.get_form(obj_id)
            if not form:
                raise NotFound(obj_id)
            # execute submitted actions
            actions = [key for key in request.keys()
                if key.startswith("action.")]
            for id in actions:
                field_id = id[7:]
                if form.fields.get(field_id, None):
                    form.compute_field(field_id, {'form': form})
            # create doc if special action _save
            if request.get("_save"):
                doc = self.app.create_document()
                doc.save(request=request, form=form, creation=True)
                redirect = doc.url
            else:
                result = form.display(edit=True)
        elif directive == "document":
            doc = self.app.get_document(obj_id)
            if not doc:
                raise NotFound(obj_id)
            editmode = (action == "edit")
            if request.get("_save"):
                doc.save(request=request)
            if request.get("_edit"):
                doc.save(request=request)
            if request.get("_delete"):
                self.app.delete_document(doc=doc)
                # TODO: use on_delete to provide redirection
                result = "deleted"
            else:
                result = doc.display(edit=editmode)
        else:
            raise NotAllowed()
        return (result, redirect)
