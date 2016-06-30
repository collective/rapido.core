import json
import string
from zope.interface import implements
from pyaml import yaml

from .interfaces import IBlock
from .elements import get_element_class
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
        record,
        edit,
        classes,
        settings,
    ):
        self.block = block
        self.record = record
        self.edit = edit
        classes = ' '.join(["rapido-block"] + classes)
        self.values = {
            '_block_name': block.id,
            '_block_action': action,
            '_block_classes': classes,
            '_block_settings': json.dumps(settings),
        }

    def __getitem__(self, key):
        if key in self.values:
            return self.values[key]
        result = None
        try:
            element = self.block.get_element(key)
            result = element.render(self.record, edit=self.edit)
        except Exception, e:
            result = "<pre>%s</pre>" % str(e)
        self.values[key] = result
        return result


class Block(FormulaContainer):
    """
    """
    implements(IBlock)

    def __init__(self, block_id, app):
        self.id = block_id
        self._app = app
        self.settings = DEFAULT_SETTINGS.copy()
        settings = yaml.load(self.app.context.get_block(block_id))
        self.settings.update(settings)
        for element in self.settings['elements']:
            if (self.settings['elements'][element].get('index_type', None)
            and element not in app.indexes):
                self.init_element(element)
        self.context = self.app.app_context.extend({
            'app': self.app,
            'block': self,
        })

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

    @property
    def code(self):
        if 'code' not in self.settings:
            try:
                self.settings['code'] = self.app.context.get_block(
                    self.id, ftype="py")
            except KeyError:
                self.settings['code'] = '# no code'
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
        try:
            self.on_display(record)
        except Exception, e:
            return "<pre>%s</pre>" % str(e)
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
        if callable(self.layout):
            form_wrapper = string.Formatter().vformat(
                BLOCK_TEMPLATE, (), values)
            form_content = self.layout(elements=values,
                context=self.context)
            return form_wrapper % form_content
        else:
            layout = BLOCK_TEMPLATE % self.layout
            return string.Formatter().vformat(layout, (), values)

    def compute_element(self, element_id, extra_context):
        context = self.context.extend(extra_context)
        return self.execute(element_id, context)

    def on_display(self, record):
        context = self.context.extend({
            'record': record,
        })
        result = self.execute('on_display', context)
        return result

    def on_save(self, record):
        context = self.context.extend({
            'record': record,
        })
        result = self.execute('on_save', context)
        return result

    def on_delete(self, record):
        context = self.context.extend({
            'record': record,
        })
        result = self.execute('on_delete', context)
        return result

    def get_element(self, element_id):
        element_settings = self.elements.get(element_id, None)
        if not element_settings:
            raise Exception("UNDEFINED ELEMENT")
        constructor = get_element_class(element_settings['type'])
        if constructor:
            element = constructor(element_id, element_settings, self)
            return element
        else:
            raise Exception("UNKNOWN ELEMENT TYPE")
