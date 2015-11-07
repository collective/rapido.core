from zope.interface import implements

from .interfaces import IRecord


class Record(object):
    implements(IRecord)

    def __init__(self, context):
        self.context = context
        self.uid = self.context.uid()
        self.id = self.context.get_item('id')
        self.app = self.context.app
        block_id = self.get_item('block')
        if block_id:
            self.block = self.app.get_block(block_id)
        else:
            self.block = None

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

    def save(self, request=None, block=None, block_id=None, creation=False):
        """ Update the record with the provided items.
        Request can be an actual HTTP request or a dictionnary.
        If a block is mentionned, formulas will be executed.
        If no block (and request is a dict), we just save the items values.
        """
        if not(block or block_id or (request and request.get('block'))):
            if type(request) is dict:
                for (key, value) in request.items():
                    self.set_item(key, value)
                self.reindex()
                return
            else:
                raise Exception("Cannot save without a block")
        if not block_id and request:
            block_id = request.get('block')
        if not block:
            block = self.app.get_block(block_id)
        self.set_item('block', block.id)

        # store submitted elements
        if request:
            for element in block.elements.keys():
                if element in request.keys():
                    self.set_item(element, request.get(element))

        # compute elements
        for (element, params) in block.elements.items():
            if (params.get('mode') == 'COMPUTED_ON_SAVE' or
            (params.get('mode') == 'COMPUTED_ON_CREATION' and creation)):
                self.set_item(
                    element, block.compute_element(element, {'record': self}))

        # compute id if record creation
        if creation:
            record_id = block.execute('record_id', self)
            if record_id:
                self.set_item('id', record_id)

        # execute on_save
        block.on_save(self)

        # compute title
        title = block.compute_element('title', {'record': self})
        if not title:
            title = block.title
        self.set_item('title', title)

        self.reindex()

    def display(self, edit=False):
        if self.block:
            return self.block.display(record=self, edit=edit)
