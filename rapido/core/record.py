from zope.interface import implements

from .interfaces import IRecord


class Record(object):
    implements(IRecord)

    def __init__(self, context):
        self.context = context
        self.uid = self.context.uid()
        self.id = self.context.get_item('id')
        self.app = self.context.app
        form_id = self.get_item('Form')
        if form_id:
            self.form = self.app.get_form(form_id)
        else:
            self.form = None

    @property
    def url(self):
        return '/'.join([
            self.app.url,
            "record",
            str(self.id),
        ])

    @property
    def title(self):
        return self.get_item('title')

    def set_item(self, name, value):
        if name == "id":
            # make sure id is unique
            duplicate = self.app.get_record(value)
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
        self.app.reindex(self)

    def save(self, request=None, form=None, form_id=None, creation=False):
        """ Update the record with the provided items.
        Request can be an actual HTTP request or a dictionnary.
        If a form is mentionned, formulas will be executed.
        If no form (and request is a dict), we just save the items values.
        """
        if not(form or form_id or (request and request.get('Form'))):
            if type(request) is dict:
                for (key, value) in request.items():
                    self.set_item(key, value)
                self.reindex()
                return
            else:
                raise Exception("Cannot save without a form")
        if not form_id and request:
            form_id = request.get('Form')
        if not form:
            form = self.app.get_form(form_id)
        self.set_item('Form', form.id)

        # store submitted fields
        if request:
            for field in form.fields.keys():
                if field in request.keys():
                    self.set_item(field, request.get(field))

        # compute fields
        for (field, params) in form.fields.items():
            if (params.get('mode') == 'COMPUTED_ON_SAVE' or
                (params.get('mode') == 'COMPUTED_ON_CREATION' and creation)):
                self.set_item(
                    field, form.compute_field(field, {'record': self}))

        # compute id if record creation
        if creation:
            id = form.execute('record_id', self)
            if id:
                self.set_item('id', id)

        # execute on_save
        form.on_save(self)

        # compute title
        title = form.compute_field('title', {'record': self})
        if not title:
            title = form.title
        self.set_item('title', title)

        self.reindex()

    def display(self, edit=False):
        if self.form:
            return self.form.display(record=self, edit=edit)
