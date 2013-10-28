from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from pyquery import PyQuery as pq

from interfaces import IForm
from rapido.core import ANNOTATION_KEY

class Form(object):
    """
    """
    implements(IForm)

    def __init__(self, context):
        self.context = context
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

    def display(self):
        layout = pq(self.layout.output)
        def process_field(index, element):
            field_id = pq(element).attr("data-rapido-field")
            return """<span class="field">
<input type="text" class="text-widget textline-field" name="%s" />
</span>
            """ % field_id
        layout("*[data-rapido-field]").replaceWith(process_field)
        return layout.html()