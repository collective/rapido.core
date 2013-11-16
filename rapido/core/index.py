from interfaces import IDocument

class Index(object):

    def reindex(self, doc):
        self.storage.reindex(doc.context)

    def reindex_all(self, rebuild=False):
        if rebuild:
            self.storage.rebuild()
        else:
            self.storage.reindex()

    def _search(self, query, sort_index=None, reverse=False):
        for record in self.storage.search(
            query,
            sort_index=sort_index,
            reverse=reverse):
            yield IDocument(record)

    def search(self, query, sort_index=None, reverse=False):
        return list(self._search(query, sort_index=sort_index,
            reverse=reverse))

    def create_index(self, fieldname, indextype, refresh=True):
        """
        """
        self.storage.create_index(fieldname, indextype)
        if refresh:
            self.reindex_all()