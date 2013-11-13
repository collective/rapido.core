from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from ..interfaces import IForm, IDatabase

class OpenForm(BrowserView):

    template = ViewPageTemplateFile('templates/openform.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = IForm(context)

    def __call__(self):
        return self.template()


class CreateDocument(BrowserView):

    def __call__(self):
        form = IForm(self.context)
        doc = form.database.create_document()
        doc.set_item('Form', form.id)
        doc.save(self.request, form=form)
        self.request.response.redirect(doc.url)


class DocumentView(BrowserView):
    implements(IPublishTraverse)

    view_template = ViewPageTemplateFile('templates/opendocument.pt')
    edit_template = ViewPageTemplateFile('templates/editdocument.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.doc = None
        self.edit_mode = False

    def publishTraverse(self, request, name):
        if name == "edit":
            self.edit_mode = True
            return self
        if name == "save":
            self.doc.save(self.request)
            return self

        doc = IDatabase(self.context).get_document(uid=int(name))
        if not doc:
            raise NotFound(self, name, request)
        self.doc = doc
        return self

    def render(self):
        if self.edit_mode:
            return self.edit_template()
        return self.view_template()

    def __call__(self):
        return self.render()


class AllDocumentsView(BrowserView):

    template = ViewPageTemplateFile('templates/documents.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.documents = IDatabase(self.context).documents()

    def __call__(self):
        return self.template()