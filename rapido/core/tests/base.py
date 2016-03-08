from zope.interface import implements
from node.base import BaseNode
from node.ext.zodb import OOBTNode
from zope.annotation.interfaces import IAttributeAnnotatable
from rapido.core.app import Context
from rapido.core.interfaces import IRapidable

FAKE1 = {
    'yaml': """target: ajax
elements:
    author:
        index_type: text
        type: TEXT
    year:
        type: NUMBER
    weight:
        type: NUMBER
    bad_field:
        type: WHATEVER
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
    something_computed:
        type: BASIC
    add_note:
        type: ACTION
    _save:
        type: ACTION
        label: Save
id: frmBook""",

    'py': """
def forever(context):
    return 'I will never change.'

def author(context):
    return "Victor Hugo"

def year(context):
    return 1845

def something_computed(context):
    return {
        'one': 1,
        'two': 2.0,
    }

def famous_quote(context):
    return 'A good plan violently executed now is better than a perfect plan executed next week.'

def add_note(context):
    context.record['note'] = "That's a good book"

def on_save(context):
    author = context.record.get('author', 'N/A')
    context.record['author'] = author.upper()""",

    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}

FAKE2 = {
    'yaml': """target: ajax
elements:
    author:
        type: TEXT
    do_something:
        type: ACTION
        label: Do""",

    'py': """
def record_id(context):
    return 'my-id'

def on_save(context):
    return "http://somewhere"

def on_delete(context):
    other = context.app.get_record('record_1')
    if other:
        other['message'] = "Good bye"
    return "http://somewhere"

def do_something(context):
    context.app.log('Hello')""",

    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}

FAKE3 = {
    'yaml': """target: ajax
elements:
    author:
        type: TEXT""",

    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}

FAKE4 = {
    'yaml': """target: ajax
elements:
    author:
        type: TEXT""",

    'py': """
def author(context):
    returm 'hello'""",

    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}

FAKE5 = {
    'yaml': """target: ajax
elements:
    author:
        type: BAD_TYPE
    _save:
        type: ACTION
        label: Save""",

    'html': """Author: {author} {_save}
<footer>Powered by Rapido</footer>"""
}

FAKE6 = {
    'yaml': """elements:
    info:
        type: BASIC""",
    'py': """def info(context):
    return {
        'title': "The Force awakens",
        'summary': "No spoil",
    }
""",
    'html': """<h1>{info[title]}</h1>
<p>{info[summary]}</p>"""
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
        self.fake_blocks = {
            'frmBook': FAKE1,
            'frmBook2': FAKE2,
            'frmBook3': FAKE3,
            'frmBook4': FAKE4,
            'frmBook5': FAKE5,
            'frmBook6': FAKE6,
        }
        self.settings = 'no_settings: {}'
        self.context = Context().extend({'app': self})

    @property
    def root(self):
        return self['root']

    def url(self):
        return "http://here"

    @property
    def blocks(self):
        return self.fake_blocks.keys()

    def get_settings(self):
        return self.settings

    def get_block(self, block_id, ftype='yaml'):
        if block_id in self.fake_blocks:
            return self.fake_blocks[block_id][ftype]
        else:
            if ftype == 'yaml':
                return 'id: ' + block_id
            else:
                raise KeyError

    def set_fake_block_data(self, block_id, ftype, data):
        self.fake_blocks[block_id][ftype] = data

    def delete_fake_block_data(self, block_id, ftype):
        del self.fake_blocks[block_id][ftype]

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
