Soup Creation
=============

    >>> from zope.interface import implements, alsoProvides, implementer, Interface
    >>> from zope.configuration.xmlconfig import XMLConfig
    >>> import zope.component
    >>> XMLConfig("meta.zcml", zope.component)()
    >>> import zope.browserpage
    >>> XMLConfig("meta.zcml", zope.browserpage)()
    >>> import zope.annotation
    >>> XMLConfig("configure.zcml", zope.annotation)()
    >>> import rapido.core
    >>> XMLConfig("configure.zcml", rapido.core)()
    >>> import rapido.souper
    >>> XMLConfig("configure.zcml", rapido.souper)()

    >>> from rapido.core.interfaces import IDatabase, IDatabasable

Create object which can store soup data:

    >>> from node.ext.zodb import OOBTNode
    >>> from node.base import BaseNode
    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> class SiteNode(OOBTNode):
    ...    implements(IAttributeAnnotatable)
    >>> root = SiteNode()

Create a persistent object that will be adapted as a rapido db:

    >>> class DatabaseNode(BaseNode):
    ...    implements(IDatabasable)
    ...    def __init__(self, uid, root):
    ...        self.uid = uid
    ...        self['root'] = root
    ...
    ...    @property
    ...    def root(self):
    ...        return self['root']
    >>> root['mydb'] = DatabaseNode(1, root)
    >>> db_obj = root['mydb']
    >>> db = IDatabase(db_obj)
    >>> db.initialize()

Create a document:

    >>> doc = db.create_document()
    >>> docid = doc.id
    >>> uid = doc.uid
    >>> doc.set_item('author', "Joseph Conrad")
    >>> doc.set_item('book_tile', "Lord Jim")
    >>> doc.get_item('author')
    'Joseph Conrad'

