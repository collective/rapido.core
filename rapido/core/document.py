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

    @property
    def url(self):
        return '/'.join([
            self.database.url,
            "document",
            str(self.id),
            ])

    @property
    def title(self):
        return self.get_item('title')

    def set_item(self, name, value):
        if name=="docid":
            # make sure id is unique
            duplicate = self.database.get_document(value)
            if duplicate and duplicate.uid != self.uid:
                value = "%s-%s" % (value, str(hash(self.context)))
            self.id = value
        self.context.set_item(name, value)

    def get_item(self, name, default=None):
        if self.context.has_item(name):
            return self.context.get_item(name)
        else:
            return default

    def remove_item(self, name):
        self.context.remove_item(name)

    def items(self):
        return self.context.items()

    def reindex(self):
        self.database.reindex(self)

    def save(self, request, form=None, form_id=None, creation=False):
        # Note: request might be a dict containing item values
        if not(form or form_id or request.get('Form')):
            raise Exception("Cannot save without a form")
        if not form_id:
            form_id = request.get('Form')
        if not form:
            form = self.database.get_form(form_id)

        # store submitted fields
        for field in form.fields.keys():
            if field in request.keys():
                self.set_item(field, request.get(field))

        # compute fields
        for (field, params) in form.fields.items():
            if (params.get('mode') == 'COMPUTED_ON_SAVE' or 
                (params.get('mode') == 'COMPUTED_ON_CREATION' and creation)):
                self.set_item(field, form.compute_field(field, context=self))

        # compute id if doc creation
        if creation:
            docid = form.execute('doc_id', self)
            if docid:
                self.set_item('docid', docid)

        # execute on_save
        form.on_save(self)

        # compute title
        title = form.compute_field('title', context=self)
        if not title:
            title = form.title
        self.set_item('title', title)
        
        self.reindex()

    def display(self, edit=False):
        if self.form:
            return self.form.display(doc=self, edit=edit)

