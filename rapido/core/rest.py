import json
from zope.interface import implements

from .interfaces import IRest
from .exceptions import NotAllowed, NotFound, Unauthorized


class Rest:
    implements(IRest)

    def __init__(self, context):
        self.context = context
        self.app = self.context

    def GET(self, path, body):
        # body will be always empty
        try:
            if not path:
                return self.app.json()

            if path[0] == "block":
                blockid = path[1]
                block = self.app.get_block(blockid)
                if not block:
                    raise NotFound(blockid)
                return block.settings

            elif path[0] == "records":
                if not self.app.acl.has_permission('view'):
                    raise Unauthorized()
                base_path = self.app.context.url() + "/record/"
                return [{
                    'id': record.id,
                    'path': base_path + record.id,
                    'items': record.items()
                } for record in self.app._records()]

            elif path[0] == "record":
                if not self.app.acl.has_permission('view'):
                    raise Unauthorized()
                id = path[1]
                record = self.app.get_record(id)
                if not record:
                    raise NotFound(id)
                if len(path) == 2:
                    return record.items()
                if len(path) == 3 and path[2] == "_full":
                    return record.block.json(record)

            else:
                raise NotAllowed()

        except IndexError:
            raise NotAllowed()

    def POST(self, path, body):
        try:
            if len(path) == 0:
                if not self.app.acl.has_permission('create_record'):
                    raise Unauthorized()
                record = self.app.create_record()
                items = json.loads(body)
                record.save(items, creation=True)
                base_path = self.app.context.url() + "/record/"
                return {
                    'success': 'created',
                    'id': record.id,
                    'path': base_path + record.id
                }
            elif path[0] == "record":
                if not self.app.acl.has_permission('edit_record'):
                    raise Unauthorized()
                id = path[1]
                record = self.app.get_record(id)
                if not record:
                    raise NotFound(id)
                items = json.loads(body)
                record.save(items)
                return {'success': 'updated'}
            elif path[0] == "records":
                if not self.app.acl.has_permission('create_record'):
                    raise Unauthorized()
                rows = json.loads(body)
                for row in rows:
                    record = self.app.create_record()
                    record.save(row, creation=True)
                return {
                    'success': 'created',
                    'total': len(rows),
                }
            elif path[0] == "search":
                if not self.app.acl.has_permission('view'):
                    raise Unauthorized()
                params = json.loads(body)
                results = self.app.search(
                    params.get("query"),
                    sort_index=params.get("sort_index"),
                    reverse=params.get("reverse")
                )
                base_path = self.app.context.url() + "/record/"
                return [{
                    'id': record.id,
                    'path': base_path + record.id,
                    'items': record.items()
                } for record in results]
            elif path[0] == "clear":
                if not self.app.acl.is_manager():
                    raise Unauthorized()
                self.app.clear_storage()
                return {
                    'success': 'clear_storage',
                }
            elif path[0] == "refresh":
                if not self.app.acl.is_manager():
                    raise Unauthorized()
                self.app.refresh()
                indexes = self.app.indexes
                indexes.sort()
                return {
                    'success': 'refresh',
                    'indexes': indexes,
                }
            else:
                raise NotAllowed()
        except IndexError:
            raise NotAllowed()

    def DELETE(self, path, body):
        if not self.app.acl.has_permission('delete'):
            raise Unauthorized()
        try:
            if path[0] == "records":
                for record in self.app.records():
                    self.app.delete_record(record=record)
                return {'success': 'deleted'}
            elif path[0] != "record":
                raise NotAllowed()
            id = path[1]
            record = self.app.get_record(id)
            if not record:
                raise NotFound(id)
            self.app.delete_record(record=record)
            return {'success': 'deleted'}
        except IndexError:
            raise NotAllowed()

    def PUT(self, path, body):
        if not self.app.acl.has_permission('create'):
            raise Unauthorized()
        try:
            if path[0] != "record":
                raise NotAllowed()
            id = path[1]
            record = self.app.create_record(id=id)
            items = json.loads(body)
            record.save(items, creation=True)
            base_path = self.app.context.url() + "/record/"
            return {
                'success': 'created',
                'id': record.id,
                'path': base_path + record.id
            }
        except IndexError:
            raise NotAllowed()

    def PATCH(self, path, body):
        if not self.app.acl.has_permission('edit'):
            raise Unauthorized()
        try:
            if path[0] != "record":
                raise NotAllowed()
            id = path[0]
            record = self.app.get_record(id)
            if not record:
                raise NotFound(id)
            items = json.loads(body)
            record.save(items)
            return {'success': 'updated'}
        except IndexError:
            raise NotAllowed()
