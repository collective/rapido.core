from zope.pagetemplate.pagetemplatefile import PageTemplateFile

class BaseField(object):
    def __init__(self, id, settings, value=None):
        self.id = id
        self.settings = settings
        self.value = value

    def render(self, edit=False):
        if edit:
            return self.edit_template(field=self)
        else:
            return self.read_template(field=self)

class TextField(BaseField):

    read_template = PageTemplateFile('templates/text-read.pt')
    edit_template = PageTemplateFile('templates/text-edit.pt')



