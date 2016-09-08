import datetime
import logging
import random
import time

from pyaml import yaml
from zope.interface import implements

from .block import Block
from .index import Index
from .interfaces import IAccessControlList
from .interfaces import IACLable
from .interfaces import IDisplayable
from .interfaces import IRapidable
from .interfaces import IRapidoApplication
from .interfaces import IRecord
from .interfaces import IRestable
from .interfaces import IStorage

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
        if 'acl' not in self.settings:
            self.settings['acl'] = {
                'rights': {
                    'reader': [],
                    'author': [],
                    'editor': [],
                },
                'roles': {},
            }
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


class SafeModules(object):
    """Manage safe modules."""

    SAFE_MODULES = {
        'datetime': datetime,
        'random': random,
        'time': time,
    }

    def __getattr__(self, name):
        """Return a module."""
        return self.SAFE_MODULES[name]

    def __setattr__(self, name, module):
        """Assign a new safe module."""
        self.SAFE_MODULES[name] = module

safe_modules = SafeModules()


class Context(object):
    """Bunch of useful objects provided by an IRapidable."""

    modules = safe_modules

    def extend(self, extra_context):
        for key in extra_context:
            setattr(self, key, extra_context[key])
        return self
