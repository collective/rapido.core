class BaseElement(object):

    def __init__(self, id, settings, block):
        self.id = id
        self.settings = settings
        self.block = block

    def get_value(self, record=None, edit=False):
        if record:
            element_value = record.get_item(self.id)
        else:
            element_value = self.block.compute_element(
                self.id, {'block': self.block})
        return element_value

    def render(self, record=None, edit=False):
        element_value = self.get_value(record, edit)
        if not element_value:
            element_value = ''
        label = self.settings.get('label', self.id)
        if edit:
            return self.edit_template.format(
                id=self.id,
                value=element_value,
                label=label,
            )
        else:
            return self.read_template.format(
                id=self.id,
                value=element_value,
                label=label,
            )


class BasicElement(BaseElement):

    read_template = """{value}"""
    edit_template = """{value}"""


class TextElement(BaseElement):

    read_template = """{value}"""
    edit_template = """<input type="text"
        name="{id}" value="{value}" />"""


class NumberElement(BaseElement):

    read_template = """{value}"""
    edit_template = """<input type="number"
        name="{id}" value="{value}" />"""


class ActionElement(BaseElement):

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


class DatetimeElement(BaseElement):

    read_template = """{value}"""
    edit_template = """<input type="date"
        name="{id}" value="{value}" />"""

    def get_value(self, record=None, edit=False):
        value = BaseElement.get_value(self, record, edit)
        return value.strftime("%Y-%m-%d")
