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
            if path[0] == "app":
                return self.app.json()

            if path[0] == "form":
                formid = path[1]
                form = self.app.get_form(formid)
                if not form:
                    raise NotFound()
                return form.json()

            if path[0] == "documents":
                return [doc.items() for doc in self.app._documents()]

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
        except Exception, e:
            return {'error': str(e)}

    def POST(self, path, body):
        try:
            if path[0] == "_create":
                doc = self.app.create_document()
                items = json.loads(body)
                doc.save(items, creation=True)
                return {'success': 'created', 'model': doc.items()}
            else:
                docid = path[1]
                doc = self.app.get_document(docid)
                if not doc:
                    raise NotFound()
                items = json.loads(body)
                doc.save(items)
                data = {'success': 'updated', 'model': doc.items()}
        except IndexError:
            raise NotAllowed()
        except Exception, e:
            return {'error': str(e)}

    def PUT(self, path, body):
        try:
            doc = self.app.create_document()
            items = json.loads(body)
            doc.save(items, creation=True)
            return {'success': 'created', 'model': doc.items()}
        except Exception, e:
            return {'error': str(e)}

    def PATCH(self, path, body):
        try:
            docid = path[0]
            doc = self.app.get_document(docid)
            if not doc:
                raise NotFound()
            items = json.loads(body)
            doc.save(items)
            data = {'success': 'updated', 'model': doc.items()}
        except Exception, e:
            return {'error': str(e)}
