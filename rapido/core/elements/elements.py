from datetime import datetime

from ..exceptions import NotFound


class BaseElement(object):

    def __init__(self, id, settings, block):
        self.id = id
        self.settings = settings
        self.block = block

    def get_value(self, record=None):
        if record and self.id in record:
            element_value = record[self.id]
        else:
            try:
                element_value = self.block.compute_element(
                    self.id, {'block': self.block, 'record': record})
            except NotFound:
                return None
        return element_value

    def process_input(self, value):
        return value

    def render(self, record=None, edit=False):
        element_value = self.get_value(record)
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

    def render(self, record=None, edit=False):
        return self.get_value(record)


class TextElement(BaseElement):

    read_template = u"""{value}"""
    edit_template = u"""<input type="text"
        name="{id}" value="{value}" />"""

    def get_value(self, record=None):
        value = BaseElement.get_value(self, record)
        return value and value.decode('utf-8')


class NumberElement(BaseElement):

    read_template = u"""{value}"""
    edit_template = u"""<input type="number"
        name="{id}" value="{value}" />"""

    def process_input(self, value):
        if '.' in value:
            return float(value)
        else:
            return int(value)

    def get_value(self, record=None):
        value = BaseElement.get_value(self, record)
        return str(value)


class ActionElement(BaseElement):

    template = u"""<input type="submit"
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

    read_template = u"""{value}"""
    edit_template = u"""<input type="date"
        name="{id}" value="{value}" />"""

    def get_value(self, record=None):
        value = BaseElement.get_value(self, record)
        if value:
            return value.strftime("%Y-%m-%d")
        else:
            return ''

    def process_input(self, value):
        return datetime.strptime(value, "%Y-%m-%d")
