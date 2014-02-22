from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

from interfaces import (
    IDatabase, IStorage, IDocument, IForm, IACLable,
    IAccessControlList, IExportable, IImportable)
from index import Index
from .security import acl_check

ANNOTATION_KEY = "RAPIDO_ANNOTATION"


class Database(Index):
    """
    """
    implements(IDatabase, IACLable, IExportable, IImportable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = PersistentDict()
        self.annotation = annotations[ANNOTATION_KEY]
        if 'available_rules' not in self.annotation:
            self.annotation['available_rules'] = {}

    def initialize(self):
        acl = self.acl
        self.storage.initialize()

    @property
    def storage(self):
        return IStorage(self.context)

    @property
    def acl(self):
        return IAccessControlList(self)

    @property
    def url(self):
        return self.context.url()

    @acl_check('create_document')
    def create_document(self, docid=None):
        record = self.storage.create()
        doc = IDocument(record)
        if not docid:
            docid = str(hash(record))
        doc.set_item('docid', docid)
        return doc

    def get_document(self, id):
        if type(id) is int:
            record = self.storage.get(id)
            if record:
                return IDocument(record)
        elif type(id) is str:
            search = self.search('docid=="%s"' % id)
            if len(search) == 1:
                return search[0]

    def _documents(self):
        for record in self.storage.documents():
            yield IDocument(record)

    def documents(self):
        return list(self._documents())

    def get_form(self, form_id):
        form_obj = self.context.get(form_id)
        if form_obj:
            return IForm(form_obj)

    @property
    def forms(self):
        return [IForm(obj) for obj in self.context.forms]

    def rules(self):
        return self.annotation['available_rules']

    def set_rule(self, rule_id, rule_settings):
        if 'available_rules' not in self.annotation:
            self.annotation['available_rules'] = {}
        self.annotation['available_rules'][rule_id] = rule_settings
        for form in self.forms:
            form.refresh_rule(rule_id)

    def remove_rule(self, rule_id):
        if self.annotation['available_rules'].get(rule_id):
            del self.annotation['available_rules'][rule_id]
        for form in self.forms:
            form.remove_rule(rule_id)

