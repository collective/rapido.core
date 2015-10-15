Soup Creation
=============

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
    >>> import rapido.core.tests
    >>> XMLConfig("configure.zcml", rapido.core.tests)()

    >>> from rapido.core.interfaces import IRapidoApplication

Create object which can store soup data::

    >>> from rapido.core.tests.base import SiteNode
    >>> root = SiteNode()

Create a persistent object that will be adapted as a rapido app::
    
    >>> from rapido.core.tests.base import SimpleRapidoApplication
    >>> root['myapp'] = SimpleRapidoApplication("testdb", root)
    >>> app_obj = root['myapp']
    >>> app = IRapidoApplication(app_obj)
    >>> app.initialize()

Create a document::

    >>> doc = app.create_document(docid='doc_1')
    >>> doc.id == 'doc_1'
    True
    >>> uid = doc.uid
    >>> doc.set_item('author', "Joseph Conrad")
    >>> doc.set_item('book_tile', "Lord Jim")
    >>> doc.get_item('author')
    'Joseph Conrad'

Documents can be found by uid or by id::
    >>> doc.reindex()
    >>> app.get_document(uid).uid == app.get_document('doc_1').uid
    True

A docid is always unique::
    >>> doc_bis = app.create_document(docid='doc_1')
    >>> doc_bis.id
    'doc_1-...'

We can use form to display documents::

    >>> from rapido.core.interfaces import IForm
    >>> form = app.get_form('frmBook')
    >>> form.display(None, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-form"\n    action="http://here/form/frmBook"\n    method="POST">Author: <input type="text"\n        name="author" value="Victor Hugo" />\n<footer>Powered by Rapido</footer></form>\n'
    >>> form.display(doc)
    u'<form\n    name="frmBook"\n    class="rapido-form"\n    action="http://here/document/doc_1"\n    method="POST">Author: Joseph Conrad\n<footer>Powered by Rapido</footer></form>\n'
    >>> form.display(doc, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-form"\n    action="http://here/document/doc_1"\n    method="POST">Author: <input type="text"\n        name="author" value="Joseph Conrad" />\n<footer>Powered by Rapido</footer></form>\n'

After saving the doc, the `on_save` method is called. In our case, the author
has been changed to uppercase::
    >>> doc.save(form=form)
    >>> doc.get_item('author')
    'JOSEPH CONRAD'

Documents can be searched::
    >>> [doc.get_item('author') for doc in app.search('docid=="doc_1"')]
    ['JOSEPH CONRAD']
    >>> [doc.get_item('author') for doc in app.search('author=="JOSEPH CONRAD"')]
    ['JOSEPH CONRAD']
    >>> [doc.get_item('author') for doc in app.search('"joseph" in author')]
    ['JOSEPH CONRAD']

Documents can be deleted::
    >>> doc2 = app.create_document()
    >>> the_id = doc2.id
    >>> app.delete_document(doc=doc2)
    >>> app.get_document(the_id) is None
    True

The doc id can be computed::
    >>> app_obj.set_fake_form_data('py', """
    ... def doc_id(context):
    ...     return 'my-id'""")
    >>> form = app.get_form('frmBook')
    >>> doc2 = app.create_document()
    >>> doc2.save({'author': "John DosPassos"}, form=form, creation=True)
    >>> doc2.id
    'my-id'
    >>> doc3 = app.create_document()
    >>> doc3.save({'author': "John DosPassos"}, form=form, creation=True)
    >>> doc3.id
    'my-id-...'

By default, the doc title is the form title::
    >>> doc.title
    'Book form'

But it can be computed::
    >>> app_obj.set_fake_form_data('py', """
    ... def title(context):
    ...     return context.document.get_item('author')""")
    >>> form = app.get_form('frmBook')
    >>> doc.save(form=form)
    >>> doc.title
    'JOSEPH CONRAD'

Fields can be computed on save::
    >>> app_obj.set_fake_form_data('py', """
    ... def famous_quote(context):
    ...     existing = context.document.get_item('famous_quote')
    ...     if not existing:
    ...         return 'A good plan violently executed now is better than a perfect plan executed next week.'
    ...     return existing + " Or next week." """)
    >>> form = app.get_form('frmBook')
    >>> doc.save(form=form)
    >>> doc.get_item('famous_quote')
    'A good plan violently executed now is better than a perfect plan executed next week.'
    >>> doc.save(form=form)
    >>> doc.get_item('famous_quote')
    'A good plan violently executed now is better than a perfect plan executed next week. Or next week.'

Fields can be computed on creation::
    >>> app_obj.set_fake_form_data('py', """
    ... def forever(context):
    ...     return 'I will never change.'""")
    >>> form = app.get_form('frmBook')
    >>> doc4 = app.create_document()
    >>> doc4.save(form=form, creation=True)
    >>> doc4.get_item('forever')
    'I will never change.'
    >>> doc.save(form=form)
    >>> doc.get_item('forever') is None
    True

Access rights
    >>> app_obj.set_fake_user("marie.curie")
    >>> app.acl.current_user()
    'marie.curie'
    >>> app.acl.has_access_right("author")
    False
    >>> doc_5 = app.create_document(docid='doc_5')
    Traceback (most recent call last):
    ...
    Unauthorized: create_document permission required
    >>> app_obj.set_fake_user("admin")
    >>> app.acl.grant_access(['marie.curie'], 'author')
    >>> app_obj.set_fake_user("marie.curie")
    >>> doc_5 = app.create_document(docid='doc_5')
    >>> doc_5.id
    'doc_5'
    >>> app_obj.set_fake_user("admin")
    >>> app.acl.grant_access(['FamousDiscoverers'], 'author')
    >>> app_obj.set_fake_user("marie.curie")
    >>> doc_6 = app.create_document(docid='doc_6')
    Traceback (most recent call last):
    ...
    Unauthorized: create_document permission required
    >>> app_obj.set_fake_groups(['FamousDiscoverers', 'FamousWomen'])
    >>> doc_6 = app.create_document(docid='doc_6')
    >>> doc_6.id
    'doc_6'