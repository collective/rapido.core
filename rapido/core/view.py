from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from interfaces import IView, IRapidoApplication
from .app import ANNOTATION_KEY as KEY
from .formula import FormulaContainer
from .rules import RuleAssignee

class View(FormulaContainer, RuleAssignee):
    """
    """
    implements(IView)

    def __init__(self, context):
        self.context = context
        self.id = self.context.id
        annotations = IAnnotations(context)
        if KEY not in annotations:
            annotations[KEY] = PersistentDict({
                'columns': [],
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
    def columns(self):
        return self.annotation["columns"]

    def set_column(self, column_id, column_settings):
        self.annotation['columns'][column_id] = column_settings
        self.app.create_index(field_id, field_settings['index_type'])

    def remove_column(self, column_id):
        if self.annotation['columns'].get(column_id):
            del self.annotation['columns'][column_id]
        #TODO: clean up index
        
    @property
    def code(self):
        return self.annotation['code']

    def set_code(self, code):
        self.annotation['code'] = code
        self.compile(recompile=True)

    @property
    def app(self):
        return IRapidoApplication(self.context.__parent__)