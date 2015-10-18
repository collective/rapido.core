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

Create a record::

    >>> record = app.create_record(id='record_1')
    >>> record.id == 'record_1'
    True
    >>> uid = record.uid
    >>> record.set_item('author', "Joseph Conrad")
    >>> record.set_item('book_tile', "Lord Jim")
    >>> record.get_item('author')
    'Joseph Conrad'

Records can be found by uid or by id::
    >>> record.reindex()
    >>> app.get_record(uid).uid == app.get_record('record_1').uid
    True

A id is always unique::
    >>> record_bis = app.create_record(id='record_1')
    >>> record_bis.id
    'record_1-...'

We can use block to display records::

    >>> from rapido.core.interfaces import IBlock
    >>> block = app.get_block('frmBook')
    >>> block.display(None, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-block"\n    action="http://here/block/frmBook"\n    method="POST">Author: <input type="text"\n        name="author" value="Victor Hugo" />\n<footer>Powered by Rapido</footer></form>\n'
    >>> block.display(record)
    u'<form\n    name="frmBook"\n    class="rapido-block"\n    action="http://here/record/record_1"\n    method="POST">Author: Joseph Conrad\n<footer>Powered by Rapido</footer></form>\n'
    >>> block.display(record, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-block"\n    action="http://here/record/record_1"\n    method="POST">Author: <input type="text"\n        name="author" value="Joseph Conrad" />\n<footer>Powered by Rapido</footer></form>\n'

After saving the record, the `on_save` method is called. In our case, the author
has been changed to uppercase::
    >>> record.save(block=block)
    >>> record.get_item('author')
    'JOSEPH CONRAD'

Records can be searched::
    >>> [record.get_item('author') for record in app.search('id=="record_1"')]
    ['JOSEPH CONRAD']
    >>> [record.get_item('author') for record in app.search('author=="JOSEPH CONRAD"')]
    ['JOSEPH CONRAD']
    >>> [record.get_item('author') for record in app.search('"joseph" in author')]
    ['JOSEPH CONRAD']

Records can be deleted::
    >>> record2 = app.create_record()
    >>> the_id = record2.id
    >>> app.delete_record(record=record2)
    >>> app.get_record(the_id) is None
    True

The record id can be computed::
    >>> app_obj.set_fake_block_data('py', """
    ... def record_id(context):
    ...     return 'my-id'""")
    >>> block = app.get_block('frmBook')
    >>> record2 = app.create_record()
    >>> record2.save({'author': "John DosPassos"}, block=block, creation=True)
    >>> record2.id
    'my-id'
    >>> record3 = app.create_record()
    >>> record3.save({'author': "John DosPassos"}, block=block, creation=True)
    >>> record3.id
    'my-id-...'

By default, the record title is the block title::
    >>> record.title
    'Book'

But it can be computed::
    >>> app_obj.set_fake_block_data('py', """
    ... def title(context):
    ...     return context.record.get_item('author')""")
    >>> block = app.get_block('frmBook')
    >>> record.save(block=block)
    >>> record.title
    'JOSEPH CONRAD'

Fields can be computed on save::
    >>> app_obj.set_fake_block_data('py', """
    ... def famous_quote(context):
    ...     existing = context.record.get_item('famous_quote')
    ...     if not existing:
    ...         return 'A good plan violently executed now is better than a perfect plan executed next week.'
    ...     return existing + " Or next week." """)
    >>> block = app.get_block('frmBook')
    >>> record.save(block=block)
    >>> record.get_item('famous_quote')
    'A good plan violently executed now is better than a perfect plan executed next week.'
    >>> record.save(block=block)
    >>> record.get_item('famous_quote')
    'A good plan violently executed now is better than a perfect plan executed next week. Or next week.'

Fields can be computed on creation::
    >>> app_obj.set_fake_block_data('py', """
    ... def forever(context):
    ...     return 'I will never change.'""")
    >>> block = app.get_block('frmBook')
    >>> record4 = app.create_record()
    >>> record4.save(block=block, creation=True)
    >>> record4.get_item('forever')
    'I will never change.'
    >>> record.save(block=block)
    >>> record.get_item('forever') is None
    True

Access rights
    >>> app_obj.set_fake_user("marie.curie")
    >>> app.acl.current_user()
    'marie.curie'
    >>> app.acl.has_access_right("author")
    False
    >>> record_5 = app.create_record(id='record_5')
    Traceback (most recent call last):
    ...
    Unauthorized: create_record permission required
    >>> app_obj.set_fake_user("admin")
    >>> app.acl.grant_access(['marie.curie'], 'author')
    >>> app_obj.set_fake_user("marie.curie")
    >>> record_5 = app.create_record(id='record_5')
    >>> record_5.id
    'record_5'
    >>> app_obj.set_fake_user("admin")
    >>> app.acl.grant_access(['FamousDiscoverers'], 'author')
    >>> app_obj.set_fake_user("marie.curie")
    >>> record_6 = app.create_record(id='record_6')
    Traceback (most recent call last):
    ...
    Unauthorized: create_record permission required
    >>> app_obj.set_fake_groups(['FamousDiscoverers', 'FamousWomen'])
    >>> record_6 = app.create_record(id='record_6')
    >>> record_6.id
    'record_6'