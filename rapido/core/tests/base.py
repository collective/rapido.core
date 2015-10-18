from zope.interface import implements
from node.base import BaseNode
from node.ext.zodb import OOBTNode
from zope.annotation.interfaces import IAttributeAnnotatable
from rapido.core.app import Context
from rapido.core.interfaces import IRapidable

FAKE = {
    'yaml': """elements:
  author:
    index_type: text
    type: TEXT
  famous_quote:
    mode: COMPUTED_ON_SAVE
    type: TEXT
  forever:
    mode: COMPUTED_ON_CREATION
    type: TEXT
  famous_quote:
    type: TEXT
    mode: COMPUTED_ON_SAVE
id: frmBook
title: Book""",

    'py': """
def forever(context):
    return 'I will never change.'

# default value for the 'author' element
def author(context):
    return "Victor Hugo"

# executed everytime we save a record with this block
def on_save(context):
    author = context.get_item('author')
    context.set_item('author', author.upper())""",

    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}


class SiteNode(OOBTNode):
    implements(IAttributeAnnotatable)


class SimpleRapidoApplication(BaseNode):
    implements(IAttributeAnnotatable, IRapidable)

    def __init__(self, id, root):
        self.id = id
        self['root'] = root
        self.fake_user = 'admin'
        self.fake_groups = []
        self.context = Context()
        self.fake_block = FAKE

    @property
    def root(self):
        return self['root']

    def url(self):
        return "http://here"

    @property
    def blocks(self):
        return ['frmBook']

    def get_settings(self):
        return """acl:
  rights:
    author: [FamousDiscoverers]
    editor: []
    manager: [admin]
    reader: []
  roles: {}"""

    def get_block(self, block_id, ftype='yaml'):
        return self.fake_block[ftype]

    def set_fake_block_data(self, ftype, data):
        self.fake_block[ftype] = data

    def current_user(self):
        return self.fake_user

    def set_fake_user(self, user):
        self.fake_user = user

    def current_user_groups(self):
        return self.fake_groups

    def set_fake_groups(self, groups):
        self.fake_groups = groups
