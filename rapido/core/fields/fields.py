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
        if not field_value:
            field_value = ''
        if edit:
            return self.edit_template.format(id=self.id, value=field_value)
        else:
            return self.read_template.format(id=self.id, value=field_value)

class TextField(BaseField):

    read_template = """{value}"""
    edit_template = """<input type="text" class="text-widget textline-field"
        name="{id}" value="{value}" />"""

class DatetimeField(BaseField):

    read_template = """{value}"""
    edit_template = """<input type="date" class="text-widget textline-field"
        name="{id}" value="{value}" />"""

