from zope.interface import implements

from .interfaces import IRecord


class Record(object):
    implements(IRecord)

    def __init__(self, context):
        self.context = context
        self.uid = self.context.uid()
        self.id = self.context.get('id')
        self.app = self.context.app
        block_id = self.get('block', None)
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

    def get(self, name, default=None):
        if name in self.context:
            return self.context[name]
        else:
            return default

    def __getitem__(self, name):
        return self.context[name]

    def __setitem__(self, name, value):
        if name == "id":
            # make sure id is unique
            duplicate = self.app.get_record(value)
            if duplicate and duplicate.uid != self.uid:
                value = "%s-%s" % (value, str(hash(self.context)))
            self.id = value
        self.context[name] = value

    def __contains__(self, name):
        return name in self.context

    def __delitem__(self, name):
        del self.context[name]

    def __iter__(self):
        return iter(self.items())

    def set_block(self, block_id):
        self.block = self.app.get_block(block_id)
        self['block'] = block_id

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
                    self[key] = value
                self.reindex()
                return
            else:
                raise Exception("Cannot save without a block")
        if not block_id and request:
            block_id = request.get('block')
        if not block:
            block = self.app.get_block(block_id)
        self['block'] = block.id

        # store submitted elements
        if request:
            for el_id in block.elements.keys():
                if el_id.startswith('_'):
                    continue
                if el_id in request.keys():
                    if type(request) is dict:
                        self[el_id] = request.get(el_id)
                    else:
                        element = block.get_element(el_id)
                        self[el_id] = element.process_input(request.get(el_id))

        # compute elements
        for (element, params) in block.elements.items():
            if (params.get('mode') == 'COMPUTED_ON_SAVE' or
            (params.get('mode') == 'COMPUTED_ON_CREATION' and creation)):
                self[element] = block.compute_element(
                    element, {'record': self})

        # compute id if record creation
        if creation:
            record_id = block.execute('record_id',
                self.app.app_context.extend({'block': block, 'record': self}))
            if record_id:
                self['id'] = record_id

        # execute on_save
        result = block.on_save(self)

        self.reindex()

        return result

    def display(self, edit=False):
        if self.block:
            return self.block.display(record=self, edit=edit)
