class BaseField(object):
    def __init__(self, id, settings, block):
        self.id = id
        self.settings = settings
        self.block = block

    def render(self, record=None, edit=False):
        if record:
            field_value = record.get_item(self.id)
        else:
            field_value = self.block.compute_field(self.id, {'block': self.block})
        if not field_value:
            field_value = ''
        label = self.settings.get('label', self.id)
        if edit:
            return self.edit_template.format(
                id=self.id,
                value=field_value,
                label=label,
            )
        else:
            return self.read_template.format(
                id=self.id,
                value=field_value,
                label=label,
            )


class BasicField(BaseField):

    read_template = """{value}"""
    edit_template = """{value}"""


class TextField(BaseField):

    read_template = """{value}"""
    edit_template = """<input type="text"
        name="{id}" value="{value}" />"""


class ActionField(BaseField):

    template = """<input type="submit"
        name="{id}" value="{label}" />"""

    def render(self, record=None, edit=False):
        if self.id.startswith('_'):
            id = self.id
        else:
            id = "action." + self.id
        label = self.settings.get('label', self.id)
        return self.template.format(
            id=id,
            label=label,
        )


class DatetimeField(BaseField):

    read_template = """{value}"""
    edit_template = """<input type="date"
        name="{id}" value="{value}" />"""
