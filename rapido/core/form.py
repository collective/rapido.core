from zope.interface import implements
from zope import component
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from pyquery import PyQuery as pq

from interfaces import IForm, IDatabase
from .database import ANNOTATION_KEY as KEY
from .fields.utils import get_field_class
from .formula import FormulaContainer
from .rules import RuleAssignee

FIELD_TYPE_MAPPING = {
    'TEXT': 'string',
    'NUMBER': 'number',
    'DATETIME': 'string',
}
FIELD_WIDGET_MAPPING = {
    'TEXT': 'text',
    'NUMBER': 'number',
    'DATETIME': 'text',
}
class Form(FormulaContainer, RuleAssignee):
    """
    """
    implements(IForm)

    def __init__(self, context):
        self.context = context
        self.id = self.context.id
        annotations = IAnnotations(context)
        if KEY not in annotations:
            annotations[KEY] = PersistentDict({
                'layout': "",
                'fields': {},
                'code': "",
                'assigned_rules': [],
            })
        self.annotation = annotations[KEY]

    @property
    def title(self):
        if hasattr(self.context, 'title'):
            return self.context.title
        else:
            return self.context.Title()

    @property
    def layout(self):
        return self.annotation['layout']

    def set_layout(self, html):
        self.annotation['layout'] = html
    
    @property
    def fields(self):
        return self.annotation["fields"]

    def set_field(self, field_id, field_settings):
        self.annotation['fields'][field_id] = field_settings
        if field_settings.get('index_type', None):
            self.database.create_index(field_id, field_settings['index_type'])

    def remove_field(self, field_id):
        if self.annotation['fields'].get(field_id):
            del self.annotation['fields'][field_id]
        #TODO: clean up index
        
    @property
    def code(self):
        return self.annotation['code']

    def set_code(self, code):
        self.annotation['code'] = code
        self.compile(recompile=True)

    @property
    def database(self):
        return IDatabase(self.context.__parent__)

    def display(self, doc=None, edit=False):
        if not self.layout:
            return ""

        layout = pq(self.layout)

        def process_field(index, element):
            field_id = pq(element).attr("data-rapido-field")
            field_settings = self.fields.get(field_id, None)
            if not field_settings:
                return "UNDEFINED FIELD"
            constructor = get_field_class(field_settings['type'])
            if constructor:
                field = constructor(field_id, field_settings, self)
                return field.render(doc, edit=edit)
            else:
                return "UNKNOWN FIELD TYPE"

        layout("*[data-rapido-field]").replaceWith(process_field)
        return layout.html()

    def compute_field(self, field_id, context=None):
        return self.execute(field_id, context)

    def on_save(self, doc):
        result = None
        for rule in self.assigned_rules:
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