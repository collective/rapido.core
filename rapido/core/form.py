from zope.interface import implements
from zope import component
from zope.event import notify
from zope.annotation.interfaces import IAnnotations
from zope.security.untrustedpython.interpreter import CompiledProgram
from persistent.dict import PersistentDict
from pyquery import PyQuery as pq

from interfaces import IForm, IDatabase
from rapido.core import ANNOTATION_KEY
from .fields.utils import get_field_class
from .events import ExecutionErrorEvent, CompilationErrorEvent

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
                'code': "",
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
        if field_settings.get('index_type', None):
            self.database.create_index(field_id, field_settings['index_type'])

    def remove_field(self, field_id):
        if self.annotations[ANNOTATION_KEY]['fields'].get(field_id):
            del self.annotations[ANNOTATION_KEY]['fields'][field_id]
        #TODO: clean up index
        
    @property
    def code(self):
        return self.annotations[ANNOTATION_KEY]['code']

    def set_code(self, code):
        self.annotations[ANNOTATION_KEY]['code'] = code
        self.compile()

    @property
    def database(self):
        return IDatabase(self.context.__parent__)

    def display(self, doc=None, edit=False):
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

    def compile(self):
        #TODO: store the compiled code in a persistent object too avoid
        # recompiling everytime
        try:
            self._compiled_code = CompiledProgram(self.code)
        except Exception, e:
            self._compiled_code = None
            notify(CompilationErrorEvent(e, self))
            return
        self._executable = {}
        self._compiled_code.exec_(self._executable)

    def execute(self, func, *args, **kwargs):
        if not hasattr(self, '_executable'):
            self.compile()
        if func in self._executable:
            try:
                return self._executable[func](*args, **kwargs)
            except Exception, e:
                notify(ExecutionErrorEvent(e, self))

    def compute_field(self, field_id, context=None):
        return self.execute(field_id, context)

    def on_save(self, doc):
        return self.execute('on_save', doc)