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
        if len(path) == 2:
            return (directive, None, None)
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
        if directive == "block":
            block = self.app.get_block(obj_id)
            if not block:
                raise NotFound(obj_id)
            result = block.display(edit=True)
        elif directive == "record":
            record = self.app.get_record(obj_id)
            if not record:
                raise NotFound(obj_id)
            editmode = (action == "edit")
            result = record.display(edit=editmode)
        elif directive == "refresh":
            self.app.refresh()
            indexes = self.app.indexes
            indexes.sort()
            result = "Refreshed (%s)" % (', '.join(indexes))
        else:
            raise NotAllowed()
        return (result, redirect)

    def POST(self, path, request):
        (directive, obj_id, action) = self._parse_path(path)
        result = ""
        redirect = ""
        if directive == "block":
            block = self.app.get_block(obj_id)
            if not block:
                raise NotFound(obj_id)
            # execute submitted actions
            actions = [key for key in request.keys()
                if key.startswith("action.")]
            for id in actions:
                element_id = id[7:]
                if block.elements.get(element_id, None):
                    block.compute_element(element_id, {'block': block})
            # create record if special action _save
            if request.get("_save"):
                record = self.app.create_record()
                record.save(request=request, block=block, creation=True)
                redirect = record.url
            else:
                result = block.display(edit=True)
        elif directive == "record":
            record = self.app.get_record(obj_id)
            if not record:
                raise NotFound(obj_id)
            editmode = (action == "edit")
            if request.get("_save"):
                record.save(request=request)
            if request.get("_edit"):
                record.save(request=request)
            if request.get("_delete"):
                self.app.delete_record(record=record)
                # TODO: use on_delete to provide redirection
                result = "deleted"
            else:
                result = record.display(edit=editmode)
        else:
            raise NotAllowed()
        return (result, redirect)
