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

Create object which can store soup data::

    >>> from node.ext.zodb import OOBTNode
    >>> from node.base import BaseNode
    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> class SiteNode(OOBTNode):
    ...    implements(IAttributeAnnotatable)
    >>> root = SiteNode()

Create a persistent object that will be adapted as a rapido db::

    >>> class SimpleDatabase(BaseNode):
    ...    implements(IAttributeAnnotatable, IDatabasable)
    ...    def __init__(self, uid, root):
    ...        self.uid = uid
    ...        self['root'] = root
    ...        self.fake_user = 'admin'
    ...        self.fake_groups = []
    ...
    ...    @property
    ...    def root(self):
    ...        return self['root']
    ...
    ...    @property
    ...    def forms(self):
    ...        return [el for el in self.values() if el.__class__.__name__=='SimpleForm']
    ...
    ...    def current_user(self):
    ...        return self.fake_user
    ...
    ...    def set_fake_user(self, user):
    ...        self.fake_user = user
    ...
    ...    def current_user_groups(self):
    ...        return self.fake_groups
    ...
    ...    def set_fake_groups(self, groups):
    ...        self.fake_groups = groups
    ...
    >>> root['mydb'] = SimpleDatabase(1, root)
    >>> db_obj = root['mydb']
    >>> db = IDatabase(db_obj)
    >>> db.initialize()

Create a document::

    >>> doc = db.create_document(docid='doc_1')
    >>> doc.id == 'doc_1'
    True
    >>> uid = doc.uid
    >>> doc.set_item('author', "Joseph Conrad")
    >>> doc.set_item('book_tile', "Lord Jim")
    >>> doc.get_item('author')
    'Joseph Conrad'

Documents can be found by uid or by id::
    >>> doc.reindex()
    >>> db.get_document(uid).uid == db.get_document('doc_1').uid
    True

A docid is always unique::
    >>> doc_bis = db.create_document(docid='doc_1')
    >>> doc_bis.id
    'doc_1-...'

We can use form to display documents::

    >>> from rapido.core.interfaces import IForm, IFormable
    >>> class SimpleForm(BaseNode):
    ...    implements(IAttributeAnnotatable, IFormable)
    ...    def __init__(self, id, title):
    ...        self.id = id
    ...        self.title = title
    >>> db_obj['frmBook'] = SimpleForm('frmBook', 'Book form')
    >>> form = IForm(db_obj['frmBook'])
    >>> form.set_field('author', {'type': 'TEXT'})
    >>> form.set_layout("""Author: <span data-rapido-field="author">author</span>""")
    >>> form.display(None, edit=True)
    u'Author: <span class="field">\n    <input type="text" class="text-widget textline-field" name="author"/>\n</span>'
    >>> form.display(doc)
    'Author: Joseph Conrad'
    >>> form.display(doc, edit=True)
    u'Author: <span class="field">\n    <input type="text" class="text-widget textline-field" name="author" value="Joseph Conrad"/>\n</span>'

A form can contain some code::
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

Default value is now 'Victor Hugo'::
    >>> form.display(None, edit=True)
    u'Author: <span class="field">\n    <input type="text" class="text-widget textline-field" name="author" value="Victor Hugo"/>\n</span>'

After saving the doc, the author has been changed to uppercase::
    >>> doc.save({}, form=form)
    >>> doc.get_item('author')
    'JOSEPH CONRAD'

Documents can be searched::
    >>> [doc.get_item('author') for doc in db.search('docid=="doc_1"')]
    ['JOSEPH CONRAD']
    >>> form.set_field('author', {'type': 'TEXT', 'index_type': 'field'})
    >>> [doc.get_item('author') for doc in db.search('author=="JOSEPH CONRAD"')]
    ['JOSEPH CONRAD']
    >>> form.set_field('author', {'type': 'TEXT', 'index_type': 'text'})
    >>> [doc.get_item('author') for doc in db.search('"joseph" in author')]
    ['JOSEPH CONRAD']

The doc id can be computed::
    >>> form.set_code("""
    ... def doc_id(context):
    ...     return 'my-id'""")
    >>> doc2 = db.create_document()
    >>> doc2.save({'author': "John DosPassos"}, form=form, creation=True)
    >>> doc2.id
    'my-id'
    >>> doc3 = db.create_document()
    >>> doc3.save({'author': "John DosPassos"}, form=form, creation=True)
    >>> doc3.id
    'my-id-...'

By default, the doc title is the form title::
    >>> doc.title
    'Book form'

But it can be computed::
    >>> form.set_code("""
    ... def title(context):
    ...     return context.get_item('author')""")
    >>> doc.save({}, form=form)
    >>> doc.title
    'JOSEPH CONRAD'

Fields can be computed on save::
    >>> form.set_field('famous_quote', {'type': 'TEXT', 'mode': 'COMPUTED_ON_SAVE'})
    >>> form.set_code("""
    ... def famous_quote(context):
    ...     existing = context.get_item('famous_quote')
    ...     if not existing:
    ...         return 'A good plan violently executed now is better than a perfect plan executed next week.'
    ...     return existing + " Or next week." """)
    >>> doc.save({}, form=form)
    >>> doc.get_item('famous_quote')
    'A good plan violently executed now is better than a perfect plan executed next week.'
    >>> doc.save({}, form=form)
    >>> doc.get_item('famous_quote')
    'A good plan violently executed now is better than a perfect plan executed next week. Or next week.'

Fields can be computed on creation::
    >>> form.set_field('forever', {'type': 'TEXT', 'mode': 'COMPUTED_ON_CREATION'})
    >>> form.set_code("""
    ... def forever(context):
    ...     return 'I will never change.'""")
    >>> doc4 = db.create_document()
    >>> doc4.save({}, form=form, creation=True)
    >>> doc4.get_item('forever')
    'I will never change.'
    >>> doc.save({}, form=form)
    >>> doc.get_item('forever') is None
    True

A rule allows to implement a given behaviour (an action to take when saving a doc,
a validation formula for a field, etc.). Rules are defined at the database level
and can then be assigned to fields, forms or views.
    >>> db.set_rule('polite', {'code': """
    ... def on_save(context):
    ...     author = context.get_item('author')
    ...     context.set_item('author', 'Monsieur ' + author)"""})
    >>> form.assign_rules(['polite'])
    >>> doc.save({}, form=form)
    >>> doc.get_item('author')
    'Monsieur JOSEPH CONRAD'

Access rights
    >>> db_obj.set_fake_user("marie.curie")
    >>> db.acl.current_user()
    'marie.curie'
    >>> db.acl.has_access_right("author")
    False
    >>> doc_5 = db.create_document(docid='doc_5')
    Traceback (most recent call last):
    ...
    NotAllowed: create_document permission required
    >>> db_obj.set_fake_user("admin")
    >>> db.acl.grant_access(['marie.curie'], 'author')
    >>> db_obj.set_fake_user("marie.curie")
    >>> doc_5 = db.create_document(docid='doc_5')
    >>> doc_5.id
    'doc_5'
    >>> db_obj.set_fake_user("admin")
    >>> db.acl.grant_access(['FamousDiscoverers'], 'author')
    >>> db_obj.set_fake_user("marie.curie")
    >>> doc_6 = db.create_document(docid='doc_6')
    Traceback (most recent call last):
    ...
    NotAllowed: create_document permission required
    >>> db_obj.set_fake_groups(['FamousDiscoverers', 'FamousWomen'])
    >>> doc_6 = db.create_document(docid='doc_6')
    >>> doc_6.id
    'doc_6'

Database can be exported
    >>> from rapido.core.interfaces import IExporter
    >>> exporter = IExporter(db)
    >>> exporter.export_database()
    {'forms': {'frmBook.py': "\ndef forever(context):\n    return 'I will never change.'", 'frmBook.yaml': u"assigned_rules:\n  - polite\nfields:\n  author:\n    index_type: text\n    type: TEXT\n  famous_quote:\n    mode: COMPUTED_ON_SAVE\n    type: TEXT\n  forever:\n    mode: COMPUTED_ON_CREATION\n    type: TEXT\nid: frmBook\ntitle: 'Book form'\n", 'frmBook.html': 'Author: <span data-rapido-field="author">author</span>'}, 'settings.yaml': u'acl:\n  rights:\n    author:\n      - FamousDiscoverers\n    editor: []\n    manager:\n      - admin\n    reader: []\n  roles: {}\n'}

