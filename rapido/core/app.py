from zope.interface import implements

from interfaces import (
    IRapidoApplication, IStorage, IDocument, IACLable,
    IAccessControlList, IExportable, IImportable, IRestable)
from index import Index
from .form import Form
from .security import acl_check


class RapidoApplication(Index):
    """
    """
    implements(IRapidoApplication, IACLable, IExportable, IImportable, IRestable)

    def __init__(self, context):
        self.context = context
        self.app_context = context.context

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

    def process(self, method, directive, obj_id, action):
        if directive == "form":
            form = self.get_form(obj_id)
            if method == "POST":
                # execute submitted actions
                actions = [key for key in self.app_context.request.keys()
                    if key.startswith("action.")]
                for id in actions:
                    field_id = id[7:]
                    if form.fields.get(field_id, None):
                        form.compute_field(field_id, {'form': form})
            result = form.display(edit=True)
        else:
            result = "Unknown directive"
        return result

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

    @acl_check('delete_document')
    def delete_document(self, docid=None, doc=None):
        if not doc:
            doc = self.get_document(docid)
        if doc:
            self.storage.delete(doc.context)

    def _documents(self):
        for record in self.storage.documents():
            yield IDocument(record)

    def documents(self):
        return list(self._documents())

    def get_form(self, form_id):
        return Form(form_id, self)

    @property
    def forms(self):
        return [self.get_form(id) for id in self.context.forms]

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

    def json(self):
        data = {"forms": [], "views": []}
        for form in self.forms:
            data["forms"].append({"id": form.id, "title": form.title})
        return data


class Context(object):
    """ bunch of useful objects provided by an IRapidable
    """

    pass
