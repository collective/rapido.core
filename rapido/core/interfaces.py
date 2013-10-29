from zope.interface import Interface


class IDatabasable(Interface):
    """ A persistent object that will support a Rapido application
    """

    def get_form(self, formid):
        """ return the form object
        """

    def get_forms(self):
        """ return all the forms
        """

    def get_view(self, formid):
        """ return the view object
        """

    def get_views(self):
        """ return all the views
        """


class IDatabase(Interface):
    """ A Rapido database
    """


class IDocument(Interface):
    """ A document
    """


class IRecordable(Interface):
    """ A record containing a document
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

class IFormable(Interface):
    """ Marker interface for a form
    """


class IForm(Interface):
    """ A Rapido form
    """


class IViewable(Interface):
    """ Marker interface for a view
    """


class IView(Interface):
    """ A Rapido view
    """


class IStorage(Interface):
    """ A storage service for Rapido documents
    """

    def initialize(self):
        """ setup the storage
        """

    def create(self):
        """ return a new document
        """

    def get(self, uid=None):
        """ return an existing document
        """

    def save(self, doc):
        """ save a document
        """

    def delete(self, doc):
        """ delete a document
        """

    def search(self, query):
        """ search for documents
        """