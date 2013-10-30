from zope.pagetemplate.pagetemplatefile import PageTemplateFile

class BaseField(object):
    def __init__(self, id, settings, value=None):
        self.id = id
        self.settings = settings
        self.value = value

    def render(self, doc=None, edit=False):
        field_value = None
        if doc:
            field_value = doc.get_item(self.id)
        if edit:
            return self.edit_template(field=self, value=field_value)
        else:
            return self.read_template(field=self, value=field_value)

class TextField(BaseField):

    read_template = PageTemplateFile('templates/text-read.pt')
    edit_template = PageTemplateFile('templates/text-edit.pt')



