from zope.interface import implements

from interfaces import (
    IRapidable, IRapidoApplication, IStorage, IRecord, IACLable,
    IAccessControlList, IRestable, IDisplayable)
from index import Index
from pyaml import yaml

from .block import Block
from .security import acl_check


class RapidoApplication(Index):
    """
    """
    implements(
        IRapidoApplication, IRapidable, IACLable, IRestable, IDisplayable)

    def __init__(self, context):
        self.context = context
        self.app_context = context.context
        self.settings = yaml.load(self.context.get_settings())

    def initialize(self):
        acl = self.acl
        self.storage.initialize()

    @property
    def storage(self):
        return IStorage(self.context)

    @property
    def acl(self):
        return IAccessControlList(self)

    @property
    def url(self):
        return self.context.url()

    def json(self):
        return self.settings

    @acl_check('create_record')
    def create_record(self, id=None):
        record = self.storage.create()
        record = IRecord(record)
        if not id:
            id = str(hash(record))
        record.set_item('id', id)
        record.reindex()
        return record

    def get_record(self, id):
        if type(id) is int:
            record = self.storage.get(id)
            if record:
                return IRecord(record)
        elif type(id) is str:
            search = self.search('id=="%s"' % id)
            if len(search) == 1:
                return search[0]

    @acl_check('delete_record')
    def delete_record(self, id=None, record=None, ondelete=True):
        if not record:
            record = self.get_record(id)
        if record:
            if ondelete and record.block:
                record.block.on_delete(record)
            self.storage.delete(record.context)

    @acl_check('modify_app')
    def clear_storage(self):
        self.storage.clear()

    @acl_check('modify_app')
    def refresh(self):
        # call the blocks so indexed elements are properly declared
        # to the index
        blocks = self.blocks
        self.reindex_all()

    def _records(self):
        for record in self.storage.records():
            yield IRecord(record)

    def records(self):
        return list(self._records())

    def get_block(self, block_id):
        return Block(block_id, self)

    @property
    def blocks(self):
        return [self.get_block(id) for id in self.context.blocks]


class Context(object):
    """ bunch of useful objects provided by an IRapidable
    """

    pass
