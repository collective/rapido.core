import string
from zope.interface import implements
from pyaml import yaml

from interfaces import IForm
from .fields.utils import get_field_class
from .formula import FormulaContainer

FIELD_TYPE_MAPPING = {
    'BASIC': 'string',
    'TEXT': 'string',
    'NUMBER': 'number',
    'DATETIME': 'string',
}
FIELD_WIDGET_MAPPING = {
    'BASIC': 'text',
    'TEXT': 'text',
    'NUMBER': 'number',
    'DATETIME': 'text',
}
DEFAULT_SETTINGS = {
    'title': "",
    'fields': {},
    'actions': {},
}

FORM_TEMPLATE = u"""<form
    name="{_form_name}"
    class="{_form_classes}"
    action="{_form_action}"
    method="POST">%s</form>
"""


class FieldDict(dict):

    def __init__(
        self,
        form,
        action,
        record=None,
        edit=True,
        classes=[]
    ):
        self.form = form
        self.record = record
        self.edit = edit
        if not action:
            action = self.form.url
        classes = ' '.join(["rapido-form"] + classes)
        self.params = {
            '_form_name': form.id,
            '_form_action': action,
            '_form_classes': classes,
        }

    def __getitem__(self, key):
        if key in self.params:
            return self.params[key]
        field_settings = self.form.fields.get(key, None)
        if not field_settings:
            return "UNDEFINED FIELD"
        constructor = get_field_class(field_settings['type'])
        if constructor:
            field = constructor(key, field_settings, self.form)
            return field.render(self.record, edit=self.edit)
        else:
            return "UNKNOWN FIELD TYPE"


class Form(FormulaContainer):
    """
    """
    implements(IForm)

    def __init__(self, id, app):
        self.id = id
        self._app = app
        self.settings = DEFAULT_SETTINGS.copy()
        settings = yaml.load(self.app.context.get_form(id))
        self.settings.update(settings)
        for field in self.settings['fields']:
            if (self.settings['fields'][field].get('index_type', None)
            and field not in app.indexes):
                self.init_field(field)

    @property
    def title(self):
        return self.settings['title']

    @property
    def layout(self):
        if 'layout' not in self.settings:
            self.settings['layout'] = self.app.context.get_form(
                self.id, ftype="html")
        return self.settings['layout']

    @property
    def fields(self):
        return self.settings['fields']

    def init_field(self, field_id):
        field = self.fields.get(field_id, None)
        if field and field.get('index_type', None):
            self.app.create_index(field_id, field['index_type'])

    def remove_field(self, field_id):
        # TODO: clean up index
        pass

    @property
    def code(self):
        if 'code' not in self.settings:
            try:
                self.settings['code'] = self.app.context.get_form(
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
        return '%s/form/%s' % (
            self.app.url,
            self.id,
        )

    def display(self, record=None, edit=False):
        if not self.layout:
            return ""
        layout = FORM_TEMPLATE % self.layout
        if record:
            action = record.url
        else:
            action = self.url
        classes = []
        target = self.settings.get('target', None)
        if target:
            classes.append('rapido-target-%s' % target)
        values = FieldDict(self, action, record, edit, classes=classes)
        return string.Formatter().vformat(layout, (), values)

    def compute_field(self, field_id, extra_context={}):
        context = self.app.app_context
        context.app = self.app
        for key in extra_context:
            setattr(context, key, extra_context[key])
        return self.execute(field_id, context)

    def on_save(self, record):
        result = self.execute('on_save', record)
        return result
