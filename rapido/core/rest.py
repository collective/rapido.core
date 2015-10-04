import json
from zope.interface import implements

from .interfaces import IRest
from .exceptions import NotAllowed, NotFound


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

            if path[0] == "form":
                formid = path[1]
                form = self.app.get_form(formid)
                if not form:
                    raise NotFound()
                return form.settings

            if path[0] == "documents":
                base_path = self.app.context.url(rest=True) + "/document/"
                return [{
                    'id': doc.id,
                    'path': base_path + doc.id,
                    'items': doc.items()
                } for doc in self.app._documents()]

            if path[0] == "document":
                docid = path[1]
                doc = self.app.get_document(docid)
                if not doc:
                    raise NotFound()
                if len(path) == 2:
                    return doc.items()
                if len(path) == 3 and path[2] == "_full":
                    return doc.form.json(doc)
        except IndexError:
            raise NotAllowed()

    def POST(self, path, body):
        try:
            if len(path) == 0:
                doc = self.app.create_document()
                items = json.loads(body)
                doc.save(items, creation=True)
                base_path = self.app.context.url(rest=True) + "/document/"
                return {
                    'success': 'created',
                    'id': doc.id,
                    'path': base_path + doc.id
                }
            elif path[0] == "document":
                docid = path[1]
                doc = self.app.get_document(docid)
                if not doc:
                    raise NotFound()
                items = json.loads(body)
                doc.save(items)
                return {'success': 'updated'}
            elif path[0] == "documents":
                rows = json.loads(body)
                for row in rows:
                    doc = self.app.create_document()
                    doc.save(row, creation=True)
                return {
                    'success': 'created',
                    'total': len(rows),
                }
            elif path[0] == "search":
                params = json.loads(body)
                results = self.app.search(
                    params.get("query"),
                    sort_index=params.get("sort_index"),
                    reverse=params.get("reverse")
                )
                base_path = self.app.context.url(rest=True) + "/document/"
                return [{
                    'id': doc.id,
                    'path': base_path + doc.id,
                    'items': doc.items()
                } for doc in results]
            else:
                raise NotAllowed()
        except IndexError:
            raise NotAllowed()

    def DELETE(self, path, body):
        try:
            if path[0] == "documents":
                for doc in self.app.documents():
                    self.app.delete_document(doc=doc)
                return {'success': 'deleted'}
            elif path[0] != "document":
                raise NotAllowed()
            docid = path[1]
            doc = self.app.get_document(docid)
            if not doc:
                raise NotFound()
            self.app.delete_document(doc=doc)
            return {'success': 'deleted'}
        except IndexError:
            raise NotAllowed()

    def PUT(self, path, body):
        try:
            if path[0] != "document":
                raise NotAllowed()
            docid = path[1]
            doc = self.app.create_document(docid=docid)
            items = json.loads(body)
            doc.save(items, creation=True)
            base_path = self.app.context.url(rest=True) + "/document/"
            return {
                'success': 'created',
                'id': doc.id,
                'path': base_path + doc.id
            }
        except IndexError:
            raise NotAllowed()

    def PATCH(self, path, body):
        try:
            if path[0] != "document":
                raise NotAllowed()
            docid = path[0]
            doc = self.app.get_document(docid)
            if not doc:
                raise NotFound()
            items = json.loads(body)
            doc.save(items)
            return {'success': 'updated'}
        except IndexError:
            raise NotAllowed()
