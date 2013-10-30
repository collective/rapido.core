from zope.interface import implements

from .interfaces import IDocument

class Document(object):
    implements(IDocument)

    def __init__(self, context):
        self.context = context
        self.uid = self.context.uid()
        self.id = self.context.get_item('docid')
        self.database = self.context.database
        form_id = self.get_item('Form')
        self.form = self.database.get_form(form_id)

    def set_item(self, name, value):
        self.context.set_item(name, value)

    def get_item(self, name, default=None):
        if self.context.has_item(name):
            return self.context.get_item(name)
        else:
            return default

    def remove_item(self, name):
        self.context.remove_item(name)

    def save(self, request, form):
        # request might be a dict containing item values
        for field in form.fields:
            if field in request.keys():
                self.set_item(field, request.get(field))

    def display(self):
        if self.form:
            return self.form.display(doc=self)

