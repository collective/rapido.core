from zope.interface import implements

from .interfaces import IDocument

class Document(object):
    implements(IDocument)

    def __init__(self, context):
        self.context = context

    def __setattr__(self, name, value):
        self.context.set_item(name, value)

    def __getattr__(self, name):
        if self.context.has_key(name):
            return self.context.get_item(name)
        else:
            raise AttributeError(name)

    def __delattr__(self, name):
        self.context.remove_item(name)

    def save(self, request, form):
        # request might be a dict containing item values
        for field in form.fields:
            if field in request.keys():
                setattr(doc, field, request.get(field))
