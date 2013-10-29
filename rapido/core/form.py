from zope.interface import implements
from zope import component
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from pyquery import PyQuery as pq

from interfaces import IForm, IDatabase
from rapido.core import ANNOTATION_KEY
from .fields.utils import get_field_class

class Form(object):
    """
    """
    implements(IForm)

    def __init__(self, context):
        self.context = context
        self.id = self.context.id
        self.annotations = IAnnotations(context)
        if ANNOTATION_KEY not in self.annotations:
            self.annotations[ANNOTATION_KEY] = PersistentDict({
                'layout': "",
                'fields': {},
            })

    @property
    def layout(self):
        return self.annotations[ANNOTATION_KEY]['layout']

    def set_layout(self, html):
        self.annotations[ANNOTATION_KEY]['layout'] = html
    
    @property
    def fields(self):
        return self.annotations[ANNOTATION_KEY]["fields"]

    def set_field(self, field_id, field_settings):
        self.annotations[ANNOTATION_KEY]['fields'][field_id] = field_settings

    @property
    def database(self):
        return IDatabase(self.context.__parent__)

    def display(self, edit=True):
        layout = pq(self.layout.output)

        def process_field(index, element):
            field_id = pq(element).attr("data-rapido-field")
            field_settings = self.fields.get(field_id, None)
            if not field_settings:
                return "UNDEFINED FIELD"
            constructor = get_field_class(field_settings['type'])
            if constructor:
                field = constructor(field_id, field_settings)
                return field.render(edit=edit)
            else:
                return "UNKNOWN FIELD TYPE"

        layout("*[data-rapido-field]").replaceWith(process_field)
        return layout.html()