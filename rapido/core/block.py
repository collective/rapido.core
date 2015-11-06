import json
import string
from zope.interface import implements
from pyaml import yaml

from interfaces import IBlock
from .elements.utils import get_element_class
from .formula import FormulaContainer

ELEMENT_TYPE_MAPPING = {
    'BASIC': 'string',
    'TEXT': 'string',
    'NUMBER': 'number',
    'DATETIME': 'string',
}
ELEMENT_WIDGET_MAPPING = {
    'BASIC': 'text',
    'TEXT': 'text',
    'NUMBER': 'number',
    'DATETIME': 'text',
}
DEFAULT_SETTINGS = {
    'title': "",
    'elements': {},
}

BLOCK_TEMPLATE = u"""<form
    name="{_block_name}"
    class="{_block_classes}"
    action="{_block_action}"
    rapido-settings='{_block_settings}'
    method="POST">%s</form>
"""


class ElementDict(dict):

    def __init__(
        self,
        block,
        action,
        record=None,
        edit=True,
        classes=[],
        settings={},
    ):
        self.block = block
        self.record = record
        self.edit = edit
        if not action:
            action = self.block.url
        classes = ' '.join(["rapido-block"] + classes)
        self.params = {
            '_block_name': block.id,
            '_block_action': action,
            '_block_classes': classes,
            '_block_settings': json.dumps(settings),
        }

    def __getitem__(self, key):
        if key in self.params:
            return self.params[key]
        element_settings = self.block.elements.get(key, None)
        if not element_settings:
            return "UNDEFINED ELEMENT"
        constructor = get_element_class(element_settings['type'])
        if constructor:
            element = constructor(key, element_settings, self.block)
            return element.render(self.record, edit=self.edit)
        else:
            return "UNKNOWN ELEMENT TYPE"


class Block(FormulaContainer):
    """
    """
    implements(IBlock)

    def __init__(self, id, app):
        self.id = id
        self._app = app
        self.settings = DEFAULT_SETTINGS.copy()
        settings = yaml.load(self.app.context.get_block(id))
        self.settings.update(settings)
        for element in self.settings['elements']:
            if (self.settings['elements'][element].get('index_type', None)
            and element not in app.indexes):
                self.init_element(element)

    @property
    def title(self):
        return self.settings['title']

    @property
    def layout(self):
        if 'layout' not in self.settings:
            self.settings['layout'] = self.app.context.get_block(
                self.id, ftype="html")
        return self.settings['layout']

    @property
    def elements(self):
        return self.settings['elements']

    def init_element(self, element_id):
        element = self.elements.get(element_id, None)
        if element and element.get('index_type', None):
            self.app.create_index(element_id, element['index_type'])

    def remove_element(self, element_id):
        # TODO: clean up index
        pass

    @property
    def code(self):
        if 'code' not in self.settings:
            try:
                self.settings['code'] = self.app.context.get_block(
                    self.id, ftype="py")
            except KeyError:
                self.settings['code'] = '# no code'
            self.compile(recompile=True)
        return self.settings['code']

    @property
    def app(self):
        return self._app

    @property
    def url(self):
        return '%s/block/%s' % (
            self.app.url,
            self.id,
        )

    def display(self, record=None, edit=False):
        if not self.layout:
            return ""
        layout = BLOCK_TEMPLATE % self.layout
        if record:
            action = record.url
        else:
            action = self.url
        classes = []
        target = self.settings.get('target', None)
        if target:
            classes.append('rapido-target-%s' % target)
        settings = self.settings.copy()
        for key in ['elements', 'layout', 'code']:
            if key in settings:
                del settings[key]
        settings['app'] = {'url': self.app.url}
        if self.app.settings.get('debug', False):
            settings['app']['debug'] = True
        values = ElementDict(
            self, action, record, edit, classes=classes, settings=settings)
        return string.Formatter().vformat(layout, (), values)

    def compute_element(self, element_id, extra_context={}):
        context = self.app.app_context
        context.app = self.app
        for key in extra_context:
            setattr(context, key, extra_context[key])
        return self.execute(element_id, context)

    def on_save(self, record):
        result = self.execute('on_save', record)
        return result

    def on_delete(self, record):
        result = self.execute('on_delete', record)
        return result
