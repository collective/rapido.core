from zope.interface import implements

from interfaces import IDatabase, IStorage, IDocument, IForm

class Database(object):
    """
    """
    implements(IDatabase)

    def __init__(self, context):
        self.context = context

    def initialize(self):
        self.storage.initialize()

    @property
    def storage(self):
        return IStorage(self.context)

    @property
    def url(self):
        return self.context.url()

    def create_document(self, docid=None):
        record = self.storage.create()
        if not docid:
            docid = str(hash(record))
        record.set_item('docid', docid)
        return IDocument(record)

    def get_document(self, id):
        if type(id) is int:
            record = self.storage.get(id)
            if record:
                return IDocument(record)

    def _documents(self):
        for record in self.storage.documents():
            yield IDocument(record)

    def documents(self):
        return list(self._documents())

    def get_form(self, form_id):
        form_obj = self.context.get(form_id)
        if form_obj:
            return IForm(form_obj)
    
    def reindex(self, doc):
        self.storage.reindex(doc.context)

    def _search(self, query, sort_index=None, reverse=False):
        for record in self.storage.search(
            query,
            sort_index=sort_index,
            reverse=reverse):
            yield IDocument(record)

    def search(self, query, sort_index=None, reverse=False):
        return list(self._search(query, sort_index=sort_index,
            reverse=reverse))