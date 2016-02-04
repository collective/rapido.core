from zope.interface import implements

from interfaces import (
    IRapidable, IRapidoApplication, IStorage, IRecord, IACLable,
    IAccessControlList, IRestable, IDisplayable)
from index import Index
import logging
from pyaml import yaml

from .block import Block

logger = logging.getLogger("Rapido")


class RapidoApplication(Index):
    """
    """
    implements(
        IRapidoApplication, IRapidable, IACLable, IRestable, IDisplayable)

    def __init__(self, context):
        self.context = context
        self.app_context = context.context
        self.settings = yaml.load(self.context.get_settings())
        self._messages = []
        self._blocks = {}

    def initialize(self):
        self.acl
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

    def create_record(self, id=None):
        record = self.storage.create()
        record = IRecord(record)
        if not id:
            id = str(hash(record))
        record['id'] = id
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

    def delete_record(self, id=None, record=None, ondelete=True):
        result = None
        if not record:
            record = self.get_record(id)
        if record:
            if ondelete and record.block:
                result = record.block.on_delete(record)
            self.storage.delete(record.context)
        return result

    def clear_storage(self):
        self.storage.clear()

    def refresh(self, rebuild=False):
        if rebuild:
            self.storage.rebuild()
        # clean up and call the blocks so indexed elements are properly
        # declared to the index
        self._blocks = {}
        self.blocks
        self.reindex_all()

    def _records(self):
        for record in self.storage.records():
            yield IRecord(record)

    def records(self):
        return list(self._records())

    def get_block(self, block_id):
        if block_id not in self._blocks:
            self._blocks[block_id] = Block(block_id, self)
        return self._blocks[block_id]

    @property
    def blocks(self):
        return [self.get_block(block_id) for block_id in self.context.blocks]

    def log(self, message):
        logger.info(message)
        self.add_message(message)

    @property
    def messages(self):
        return self._messages

    def add_message(self, message):
        self._messages.append(message)


class Context(object):
    """ bunch of useful objects provided by an IRapidable
    """

    def extend(self, extra_context):
        for key in extra_context:
            setattr(self, key, extra_context[key])
        return self
