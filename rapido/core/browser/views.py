from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from ..interfaces import IForm

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
        doc.Form = form.id
        doc.save(self.request, form)
        import pdb; pdb.set_trace( )