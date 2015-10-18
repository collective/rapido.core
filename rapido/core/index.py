from interfaces import IRecord


class Index(object):

    def reindex(self, record):
        self.storage.reindex(record.context)

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
            yield IRecord(record)

    def search(self, query, sort_index=None, reverse=False):
        return list(self._search(query, sort_index=sort_index,
            reverse=reverse))

    @property
    def indexes(self):
        return self.storage.indexes

    def create_index(self, elementname, indextype, refresh=True):
        """
        """
        self.storage.create_index(elementname, indextype)
        if refresh:
            self.reindex_all()
