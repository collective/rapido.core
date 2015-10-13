from zope.interface import implements

from interfaces import (
    IRapidable, IRapidoApplication, IStorage, IDocument, IACLable,
    IAccessControlList, IRestable)
from index import Index
from pyaml import yaml

from .form import Form
from .security import acl_check


class RapidoApplication(Index):
    """
    """
    implements(IRapidoApplication, IRapidable, IACLable, IRestable)

    def __init__(self, context):
        self.context = context
        self.app_context = context.context
        self.settings = yaml.load(self.context.get_settings())

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
        result = ""
        redirect = ""
        request = self.app_context.request
        if directive == "form":
            form = self.get_form(obj_id)
            if method == "POST":
                # execute submitted actions
                actions = [key for key in request.keys()
                    if key.startswith("action.")]
                for id in actions:
                    field_id = id[7:]
                    if form.fields.get(field_id, None):
                        form.compute_field(field_id, {'form': form})
                # create doc if special action _save
                if request.get("_save"):
                    doc = self.create_document()
                    doc.save(request=request, form=form, creation=True)
                    redirect = doc.url
                else:
                    result = form.display(edit=True)
            else:
                result = form.display(edit=True)
        elif directive == "document":
            doc = self.get_document(obj_id)
            editmode = (action == "edit")
            if method == "POST" and request.get("_save"):
                doc.save(request=request)
            if method == "POST" and request.get("_delete"):
                self.delete_document(doc=doc)
                # TODO: use on_delete to provide redirection
                result = "deleted"
            else:
                result = doc.display(edit=editmode)
        else:
            result = "Unknown directive"
        return (result, redirect)

    def json(self):
        return self.settings

    @acl_check('create_document')
    def create_document(self, docid=None):
        record = self.storage.create()
        doc = IDocument(record)
        if not docid:
            docid = str(hash(record))
        doc.set_item('docid', docid)
        doc.reindex()
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


class Context(object):
    """ bunch of useful objects provided by an IRapidable
    """

    pass
