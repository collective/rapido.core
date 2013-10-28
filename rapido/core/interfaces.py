from zope.interface import Interface

class ILayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


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
    """
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
