from zope.interface import implements

from .interfaces import IDisplay
from .exceptions import NotAllowed, NotFound, Unauthorized


class Display(object):
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
            try:
                result = block.display(edit=True)
            except KeyError:
                raise NotFound(obj_id)
        elif directive == "record":
            if not self.app.acl.has_permission('view'):
                raise Unauthorized()
            record = self.app.get_record(obj_id)
            if not record:
                raise NotFound(obj_id)
            editmode = (action == "edit")
            result = record.display(edit=editmode)
        elif directive == "refresh":
            if not self.app.acl.is_manager():
                raise Unauthorized()
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
            # execute submitted actions
            actions = [key for key in request.keys()
                if key.startswith("action.")]
            for action_id in actions:
                element_id = action_id[7:]
                if block.elements.get(element_id, None):
                    redirect = block.compute_element(
                        element_id, {'block': block})
            # create record if special action _save
            if request.get("_save"):
                if not self.app.acl.has_permission('create'):
                    raise Unauthorized()
                record = self.app.create_record()
                record['_author'] = [self.app.acl.current_user(), ]
                record.save(request=request, block=block, creation=True)
                redirect = record.url
            else:
                try:
                    result = block.display(edit=True)
                except KeyError:
                    raise NotFound(obj_id)
        elif directive == "record":
            record = self.app.get_record(obj_id)
            if not record:
                raise NotFound(obj_id)
            editmode = (action == "edit")
            if request.get("_save"):
                if not self.app.acl.has_permission('edit', record):
                    raise Unauthorized()
                record.save(request=request)
                result = record.display(edit=editmode)
            elif request.get("_edit"):
                if not self.app.acl.has_permission('edit', record):
                    raise Unauthorized()
                result = record.display(edit=True)
            elif request.get("_delete"):
                if not self.app.acl.has_permission('delete', record):
                    raise Unauthorized()
                self.app.delete_record(record=record)
                # TODO: use on_delete to provide redirection
                result = "deleted"
            else:
                if not self.app.acl.has_permission('view'):
                    raise Unauthorized()
                result = record.display(edit=editmode)
        else:
            raise NotAllowed()
        return (result, redirect)
