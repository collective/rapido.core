from zope.interface import implements
from node.base import BaseNode
from node.ext.zodb import OOBTNode
from zope.annotation.interfaces import IAttributeAnnotatable
from rapido.core.app import Context
from rapido.core.interfaces import IRapidable

SCRIPTS = {}
FAKE1 = {
    'yaml': """target: ajax
elements:
    author:
        index_type: text
        type: TEXT
    year: NUMBER
    weight: NUMBER
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
    publication: DATETIME
    something_computed: BASIC
    add_note: ACTION
    go_to_bed: ACTION
    _save:
        type: ACTION
        label: Save
id: frmBook""",
    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}
def fake1_forever(context):
    return 'I will never change.'

def fake1_author(context):
    return "Victor Hugo"

def fake1_year(context):
    return 1845

def fake1_something_computed(context):
    return {
        'one': 1,
        'two': 2.0,
    }

def fake1_famous_quote(context):
    return 'A good plan violently executed now is better than a perfect plan executed next week.'

def fake1_add_note(context):
    context.record['note'] = "That's a good book"

def fake1_go_to_bed(context):
    return 'http://localhost/bed'

def fake1_on_save(context):
    author = context.record.get('author', 'N/A')
    context.record['author'] = author.upper()

SCRIPTS['frmBook'] = {
    'forever': fake1_forever,
    'author': fake1_author,
    'year': fake1_year,
    'something_computed': fake1_something_computed,
    'famous_quote': fake1_famous_quote,
    'add_note': fake1_add_note,
    'go_to_bed': fake1_go_to_bed,
    'on_save': fake1_on_save,
}
FAKE2 = {
    'yaml': """target: ajax
elements:
    author: TEXT
    do_something:
        type: ACTION
        label: Do""",
    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}
def fake2_record_id(context):
    return 'my-id'

def fake2_on_save(context):
    return "http://somewhere"

def fake2_on_delete(context):
    other = context.app.get_record('record_1')
    if other:
        other['message'] = "Good bye"
    return "http://somewhere"

def fake2_do_something(context):
    context.app.log('Hello')

SCRIPTS['frmBook2'] = {
    'record_id': fake2_record_id,
    'on_save': fake2_on_save,
    'on_delete': fake2_on_delete,
    'do_something': fake2_do_something,
}
FAKE3 = {
    'yaml': """target: ajax
elements:
    author: TEXT""",
    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}

FAKE4 = {
    'yaml': """target: ajax
elements:
    author: TEXT""",
    'html': """Author: {author}
<footer>Powered by Rapido</footer>"""
}

SCRIPTS['frmBook4'] = {
    'rapido_error': 'Syntax error at line 42'
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
    info: BASIC""",
    'html': """<h1>{info[title]}</h1>
<p>{info[summary]}</p>"""
}

def fake6_info(context):
    return {
        'title': "The Force awakens",
        'summary': "No spoil",
    }

SCRIPTS['frmBook6'] = {
    'info': fake6_info,
}

FAKE7 = {
    'yaml': """target: ajax
elements:
    author: TEXT
    message: BASIC""",
    'html': """<p>Author: {author}</p>
<footer>{message}</footer>"""
}

def fake7_message(context):
    if context.record:
        return "Bonjour " + context.record['author']
    else:
        return "No author"

SCRIPTS['frmBook7'] = {
    'message': fake7_message,
}

FAKE8 = {
    'yaml': """target: ajax
elements:
    message: BASIC""",
}

def fake8_message(context):
    return "bacon"

SCRIPTS['frmBook8'] = {
    'message': fake8_message,
}

FAKE9 = {
    'yaml': """target: ajax
elements:
    a_number: BASIC
    a_date: BASIC""",
    'html': """<p>Random: {a_number}</p>
<p>Date: {a_date}</p>""",
}

def fake9_a_number(context):
    if context.modules.re:
        return context.modules.random.random()

def fake9_a_date(context):
    return context.modules.datetime.date.today().strftime("%Y-%m-%d")

SCRIPTS['frmBook9'] = {
    'a_number': fake9_a_number,
    'a_date': fake9_a_date,
}

FAKE10 = {
    'yaml': """elements:
    message: BASIC""",
    'html': """<p>{message}</p>""",
}

def fake10_on_display(context):
    context.hero = "John Snow"

def fake10_message(context):
    return "You know nothing, " + context.hero

SCRIPTS['block10'] = {
    'on_display': fake10_on_display,
    'message': fake10_message,
}

FAKE11 = {
    'yaml': """elements:
    message: BASIC
view_permission:
    isaac.newton""",
    'html': """<p>{message}</p>""",
}

def fake11_message(context):
    return "You know nothing, John Snow"

SCRIPTS['block11'] = {
    'message': fake11_message,
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
            'frmBook7': FAKE7,
            'frmBook8': FAKE8,
            'frmBook9': FAKE9,
            'block10': FAKE10,
            'block11': FAKE11,
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
        if block_id == 'frmBook8' and ftype == 'html':
            return lambda elements, context: 'France is ' + elements['message']
        if block_id in self.fake_blocks:
            return self.fake_blocks[block_id][ftype]
        else:
            if ftype == 'yaml':
                return 'id: ' + block_id
            else:
                raise KeyError

    def get_script(self, block):
        return SCRIPTS[block]

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
