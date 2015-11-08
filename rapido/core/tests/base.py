from zope.interface import implements
from node.base import BaseNode
from node.ext.zodb import OOBTNode
from zope.annotation.interfaces import IAttributeAnnotatable
from rapido.core.app import Context
from rapido.core.interfaces import IRapidable

FAKE = {
    'yaml': """target: ajax
debug: true
elements:
    author:
        index_type: text
        type: TEXT
    year:
        type: NUMBER
    famous_quote:
        mode: COMPUTED_ON_SAVE
        type: TEXT
    forever:
        mode: COMPUTED_ON_CREATION
        type: TEXT
    famous_quote:
        type: TEXT
        mode: COMPUTED_ON_SAVE
    publication:
        type: DATETIME
    do_something:
        type: ACTION
        label: Do
    _save:
        type: ACTION
        label: Save
id: frmBook
title: Book""",

    'py': """
def forever(context):
    return 'I will never change.'

def do_something(context):
    context.app.log('Hello')

# default value for the 'author' element
def author(context):
    return "Victor Hugo"

def year(context):
    return 1845

# executed everytime we save a record with this block
def on_save(context):
    author = context['author']
    context['author'] = author.upper()""",

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
    editor: [marie.curie]
    reader: [isaac.newton]
  roles: {"boss": ["marie.curie"]}"""

    def get_block(self, block_id, ftype='yaml'):
        if block_id == 'frmBook':
            return self.fake_block[ftype]
        else:
            if ftype == 'yaml':
                return 'id: ' + block_id
            else:
                raise KeyError

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

    def is_manager(self):
        if self.fake_user == 'admin':
            return True
        return False
