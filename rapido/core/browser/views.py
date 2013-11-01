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
        doc.save(self.request, form)
        self.request.response.redirect("../document/" + str(doc.uid))


class DocumentView(BrowserView):
    implements(IPublishTraverse)

    template = ViewPageTemplateFile('templates/opendocument.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.doc = None

    def publishTraverse(self, request, name):
        doc = IDatabase(self.context).get_document(uid=int(name))
        if not doc:
            raise NotFound(self, name, request)
        self.doc = doc
        return self

    def render(self):
        return self.template()