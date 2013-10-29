from zope.interface import implements

from interfaces import IDatabase, IStorage, IDocument

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
        