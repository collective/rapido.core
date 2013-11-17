from zope.pagetemplate.pagetemplatefile import PageTemplateFile

class BaseField(object):
    def __init__(self, id, settings, form):
        self.id = id
        self.settings = settings
        self.form = form

    def render(self, doc=None, edit=False):
        if doc:
            field_value = doc.get_item(self.id)
        else:
            field_value = self.form.compute_field(self.id, context=self.form)
        if edit:
            return self.edit_template(field=self, value=field_value)
        else:
            return self.read_template(field=self, value=field_value)

class TextField(BaseField):

    read_template = PageTemplateFile('templates/text-read.pt')
    edit_template = PageTemplateFile('templates/text-edit.pt')



