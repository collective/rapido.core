from zope.interface import implements

from interfaces import IDatabase, IStorage, IDocument, IForm

class Database(object):
    """
    """
    implements(IDatabase)

    def __init__(self, context):
        self.context = context

    @property
    def storage(self):
        return IStorage(self.context)

    def create_document(self, docid=None):
        record = self.storage.create()
        if not docid:
            docid = str(hash(record))
        record.set_item('docid', docid)
        return IDocument(record)

    def get_document(self, docid=None, uid=None):
        if uid:
            record = self.storage.get(uid)
            if record:
                return IDocument(record)

    def get_form(self, form_id):
        form_obj = self.context.get(form_id)
        if form_obj:
            return IForm(form_obj)
        