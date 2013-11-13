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

    >>> class SimpleDatabase(BaseNode):
    ...    implements(IDatabasable)
    ...    def __init__(self, uid, root):
    ...        self.uid = uid
    ...        self['root'] = root
    ...
    ...    @property
    ...    def root(self):
    ...        return self['root']
    >>> root['mydb'] = SimpleDatabase(1, root)
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

We can use form to display documents:

    >>> from rapido.core.interfaces import IForm, IFormable
    >>> class SimpleForm(BaseNode):
    ...    implements(IAttributeAnnotatable, IFormable)
    ...    def __init__(self, id):
    ...        self.id = id
    >>> db_obj['frmBook'] = SimpleForm('frmBook')
    >>> form = IForm(db_obj['frmBook'])
    >>> form.set_field('author', {'type': 'TEXT'})
    >>> form.set_layout("""Author: <span data-rapido-field="author">author</span>""")
    >>> form.display(None, edit=True)
    u'Author: <span class="field">\n    <input type="text" class="text-widget textline-field" name="author"/>\n</span>'
    >>> form.display(doc)
    'Author: Joseph Conrad'
    >>> form.display(doc, edit=True)
    u'Author: <span class="field">\n    <input type="text" class="text-widget textline-field" name="author" value="Joseph Conrad"/>\n</span>'

A form can contain some code:
    >>> form = IForm(db_obj['frmBook'])
    >>> form.set_code("""
    ... # default value for the 'author' field
    ... def author(context):
    ...     return "Victor Hugo"
    ...
    ... # executed everytime we save a doc with this form
    ... def on_save(context):
    ...     author = context.get_item('author')
    ...     context.set_item('author', author.upper())""")

Default value is now 'Victor Hugo':
    >>> form.display(None, edit=True)
    u'Author: <span class="field">\n    <input type="text" class="text-widget textline-field" name="author" value="Victor Hugo"/>\n</span>'

After saving the doc, the author has been changed to uppercase:
    >>> doc.save({}, form=form)
    >>> doc.get_item('author')
    'JOSEPH CONRAD'
