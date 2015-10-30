from zope.interface import Interface


class IRapidable(Interface):
    """ A persistent object that will support a Rapido application
    """

    def get_block(self, blockid):
        """ return the block object
        """

    def get_blocks(self):
        """ return all the blocks
        """

    def get_view(self, blockid):
        """ return the view object
        """

    def get_views(self):
        """ return all the views
        """


class IRapidoApplication(Interface):
    """ A Rapido app
    """


class IRecord(Interface):
    """ A record
    """


class IRecordable(Interface):
    """ Something able to handle a record
    """

    def set_item(self, name, value):
        """ set an item value
        """

    def get_item(self, name):
        """ return an item value
        """

    def has_item(self, name):
        """ test if item exists
        """

    def remove_item(self, name):
        """ remove an item
        """

    def uid(self):
        """ return internal identifier
        """


class IBlock(Interface):
    """ A Rapido block
    """


class IStorage(Interface):
    """ A storage service for Rapido records
    """

    def initialize(self):
        """ setup the storage
        """

    def create(self):
        """ return a new record
        """

    def get(self, uid=None):
        """ return an existing record
        """

    def save(self, record):
        """ save a record
        """

    def delete(self, record):
        """ delete a record
        """

    def search(self, query):
        """ search for records
        """


class IACLable(Interface):
    """ Marker interface for an access control
    """


class IAccessControlList(Interface):
    """ An access control list manager
    """


class IRestable(Interface):
    """ Marker interface for REST-able
    """


class IRest(Interface):
    """ Rest features
    """


class IDisplayable(Interface):
    """ Marker interface for Display-able
    """


class IDisplay(Interface):
    """ Display features
    """
