import string
from zope.interface import implements
from pyaml import yaml

from interfaces import IForm
from .fields.utils import get_field_class
from .formula import FormulaContainer
from .rules import RuleAssignee

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
    'assigned_rules': [],
    'actions': {},
}

FORM_TEMPLATE = """<form
    name="{_form_name}"
    class="{_form_classes}"
    action="{_form_action}"
    method="{_form_method}">%s</form>
"""


class FieldDict(dict):

    def __init__(
        self,
        form,
        doc=None,
        edit=True,
        action=None,
        classes=[],
        method="POST"
    ):
        self.form = form
        self.doc = doc
        self.edit = edit
        if not action:
            action = self.form.url
        classes = ' '.join(["rapido-form"] + classes)
        self.params = {
            '_form_name': form.id,
            '_form_action': action,
            '_form_classes': classes,
            '_form_method': method,
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
            return field.render(self.doc, edit=self.edit)
        else:
            return "UNKNOWN FIELD TYPE"


class Form(FormulaContainer, RuleAssignee):
    """
    """
    implements(IForm)

    def __init__(self, id, app):
        self.id = id
        self._app = app
        self.settings = DEFAULT_SETTINGS.copy()
        settings = yaml.load(self.app.context.get_form(id))
        self.settings.update(settings)

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
            self.settings['code'] = self.app.context.get_form(
                self.id, ftype="py")
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

    def display(self, doc=None, edit=False):
        if not self.layout:
            return ""
        layout = FORM_TEMPLATE % self.layout
        values = FieldDict(self, doc, edit)
        return string.Formatter().vformat(layout, (), values)

    def compute_field(self, field_id, context=None):
        return self.execute(field_id, context)

    def on_save(self, doc):
        result = None
        for rule in self.settings['assigned_rules']:
            result = self.execute_rule(rule, 'on_save', doc)
        result = self.execute('on_save', doc)
        return result

    def json(self, context=None):
        if not context:
            context = self
        data = {
            "layout": self.layout,
            "schema": {
                "type": "object",
                "title": self.title,
                "properties": {},
            },
            "form": [{
                "type": "submit",
                "style": "btn-info",
                "title": "Save"
            }],
        }
        properties = {}
        fields = []
        for field_id in self.fields.keys():
            settings = self.fields[field_id]
            properties[field_id] = {
                "title": settings.get('title', field_id),
                "description": settings.get('description'),
                "type": FIELD_TYPE_MAPPING.get(settings['type'], 'TEXT'),
            }
            field = {
                'key': field_id,
                'type': FIELD_WIDGET_MAPPING.get(settings['type'], 'TEXT'),
            }

            # insert computed settings
            extra_settings = self.execute(field_id + '_settings', context)
            if extra_settings:
                if extra_settings.get("properties"):
                    for (key, value) in extra_settings["properties"].items():
                        properties[field_id][key] = value
                if extra_settings.get("form"):
                    for (key, value) in extra_settings["form"].items():
                        field[key] = value

            fields.append(field)

        data["schema"]["properties"] = properties
        data["form"] = data["form"] + fields

        return data
