import json
from zope.interface import implements

from .interfaces import IRest
from .exceptions import NotAllowed, NotFound, Unauthorized


class Rest(object):
    implements(IRest)

    def __init__(self, context):
        self.context = context
        self.app = self.context

    def GET(self, path, body):
        # body will be always empty
        try:
            if not path:
                return self.app.settings

            if path[0] == "block":
                blockid = path[1]
                block = self.app.get_block(blockid)
                if len(path) == 2:
                    return block.settings
                elif len(path) == 3:
                    element_id = path[2]
                    return block.compute_element(element_id, {'block': block})
                else:
                    raise NotAllowed()

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
                record_id = path[1]
                record = self.app.get_record(record_id)
                if not record:
                    raise NotFound(record_id)
                if len(path) == 2:
                    return record.items()
            else:
                raise NotAllowed()

        except IndexError:
            raise NotAllowed()

    def POST(self, path, body):
        try:
            if not path:
                if not self.app.acl.has_permission('create'):
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
                record_id = path[1]
                record = self.app.get_record(record_id)
                if not record:
                    raise NotFound(record_id)
                if not self.app.acl.has_permission('edit', record):
                    raise Unauthorized()
                items = json.loads(body)
                record.save(items)
                return {'success': 'updated'}
            elif path[0] == "records":
                if not self.app.acl.has_permission('create'):
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
            elif path[0] == "refresh":
                if not self.app.acl.is_manager():
                    raise Unauthorized()
                if body:
                    params = json.loads(body)
                    rebuild = params and params['rebuild']
                else:
                    rebuild = False
                self.app.refresh(rebuild=rebuild)
                indexes = self.app.indexes
                indexes.sort()
                return {
                    'success': 'refresh',
                    'indexes': indexes,
                }
            elif path[0] == "block":
                blockid = path[1]
                block = self.app.get_block(blockid)
                if len(path) == 3:
                    element_id = path[2]
                    return block.compute_element(element_id, {'block': block})
                else:
                    raise NotAllowed()
            else:
                raise NotAllowed()
        except IndexError:
            raise NotAllowed()

    def DELETE(self, path, body):
        try:
            if path[0] == "records":
                if not self.app.acl.has_permission('delete'):
                    raise Unauthorized()
                self.app.clear_storage()
                return {'success': 'deleted'}
            elif path[0] != "record":
                raise NotAllowed()
            record_id = path[1]
            record = self.app.get_record(record_id)
            if not record:
                raise NotFound(record_id)
            if not self.app.acl.has_permission('delete', record):
                raise Unauthorized()
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
            record_id = path[1]
            existing = self.app.get_record(record_id)
            if existing:
                raise NotAllowed()
            record = self.app.create_record(id=record_id)
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
        try:
            if path[0] != "record":
                raise NotAllowed()
            record_id = path[1]
            record = self.app.get_record(record_id)
            if not record:
                raise NotFound(record_id)
            if not self.app.acl.has_permission('edit', record):
                raise Unauthorized()
            items = json.loads(body)
            record.save(items)
            return {'success': 'updated'}
        except IndexError:
            raise NotAllowed()
