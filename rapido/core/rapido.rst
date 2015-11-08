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
    >>> root['myapp'] = SimpleRapidoApplication("testapp", root)
    >>> app_obj = root['myapp']
    >>> app = IRapidoApplication(app_obj)
    >>> app.initialize()

Create a record::

    >>> record = app.create_record(id='record_1')
    >>> record.id == 'record_1'
    True
    >>> uid = record.uid
    >>> record['author'] = "Joseph Conrad"
    >>> record['book_tile'] = "Lord Jim"
    >>> record['author']
    'Joseph Conrad'
    >>> record['not_important'] = 2
    >>> 'not_important' in record
    True
    >>> del record['not_important']
    >>> [key for key in record]
    ['book_tile', 'id', 'author']

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
    u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/block/frmBook"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="Victor Hugo" />\n<footer>Powered by Rapido</footer></form>\n'
    >>> block.display(record)
    u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: Joseph Conrad\n<footer>Powered by Rapido</footer></form>\n'
    >>> block.display(record, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="Joseph Conrad" />\n<footer>Powered by Rapido</footer></form>\n'

After saving the record, the `on_save` method is called. In our case, the author
has been changed to uppercase::
    >>> record.save(block=block)
    >>> record['author']
    'JOSEPH CONRAD'

Records can be searched::
    >>> [record['author'] for record in app.search('id=="record_1"')]
    ['JOSEPH CONRAD']
    >>> [record['author'] for record in app.search('author=="JOSEPH CONRAD"')]
    ['JOSEPH CONRAD']
    >>> [record['author'] for record in app.search('"joseph" in author')]
    ['JOSEPH CONRAD']

Records can be deleted::
    >>> record2 = app.create_record()
    >>> the_id = record2.id
    >>> app.delete_record(record=record2)
    >>> app.get_record(the_id) is None
    True
    >>> record22 = app.create_record()
    >>> the_id = record22.id
    >>> app.delete_record(id=the_id)
    >>> app.get_record(the_id) is None
    True

The record id can be computed::
    >>> app_obj.set_fake_block_data('py', """
    ... def author(context):
    ...     return "Victor Hugo"
    ... def record_id(context):
    ...     return 'my-id'""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> record2 = app.create_record()
    >>> record2.save({'author': "John DosPassos"}, block=block, creation=True)
    >>> record2.id
    'my-id'
    >>> record3 = app.create_record()
    >>> record3.save({'author': "John DosPassos"}, block_id="frmBook", creation=True)
    >>> record3.id
    'my-id-...'

By default, the record title is the block title::
    >>> record.title
    'Book'

But it can be computed::
    >>> app_obj.set_fake_block_data('py', """
    ... def author(context):
    ...     return "Victor Hugo"
    ... def title(context):
    ...     return context.record['author']""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> record.save(block=block)
    >>> record.title
    'JOSEPH CONRAD'

Python errors handling
    >>> app_obj.set_fake_block_data('py', """
    ... def title(context):
    ...     returm context.record['author']""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> record.save(block=block)
    >>> app.messages[0]
    "Rapido compilation error - testapp:\nin frmBook, at line 3: invalid syntax\n    returm context.record['author']\n-----------------^"
    >>> app_obj.set_fake_block_data('py', """
    ... def title(context):
    ...     return context.not_a_method()""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> record.save(block=block)
    >>> app.messages[1]
    'Rapido execution error - testapp:\n   \'Context\' object has no attribute \'not_a_method\'\n   File "frmBook.py", line 3, in title'
    >>> app_obj.set_fake_block_data('py', """
    ... def title(context):
    ...     return context.record['author']""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')

Elements can be computed on save::
    >>> app_obj.set_fake_block_data('py', """
    ... def famous_quote(context):
    ...     existing = context.record['famous_quote']
    ...     if not existing:
    ...         return 'A good plan violently executed now is better than a perfect plan executed next week.'
    ...     return existing + " Or next week." """)
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> record.save(block=block)
    >>> record['famous_quote']
    'A good plan violently executed now is better than a perfect plan executed next week.'
    >>> record.save(block=block)
    >>> record['famous_quote']
    'A good plan violently executed now is better than a perfect plan executed next week. Or next week.'

Elements can be computed on creation::
    >>> app_obj.set_fake_block_data('py', """
    ... def forever(context):
    ...     return 'I will never change.'""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> record4 = app.create_record()
    >>> record4.save(block=block, creation=True)
    >>> record4['forever']
    'I will never change.'
    >>> record.save(block=block)
    >>> record.get('forever') is None
    True

Datetime and number fields
    >>> app_obj.set_fake_block_data('py', """
    ... def author(context):
    ...     return "Victor Hugo"
    ... def year(context):
    ...     return 1845""")
    >>> app_obj.set_fake_block_data('html', """Author: {author}
    ... {publication} {year}<footer>Powered by Rapido</footer>""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> block.display(None, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/block/frmBook"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="Victor Hugo" />\n<input type="date"\n        name="publication" value="" /> <input type="number"\n        name="year" value="1845" /><footer>Powered by Rapido</footer></form>\n'

    >>> app_obj.set_fake_block_data('html', """Author: {author}
    ... <footer>Powered by Rapido</footer>""")
    >>> app_obj.set_fake_block_data('py', "")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')

Actions
    >>> app_obj.set_fake_block_data('html', """Author: {author}
    ... {do_something} {_save}<footer>Powered by Rapido</footer>""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')
    >>> block.display(None, edit=True)
    u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/block/frmBook"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="" />\n<input type="submit"\n        name="action.do_something" value="Do" /> <input type="submit"\n        name="_save" value="Save" /><footer>Powered by Rapido</footer></form>\n'
    >>> app_obj.set_fake_block_data('html', """Author: {author}
    ... <footer>Powered by Rapido</footer>""")
    >>> del app._blocks['frmBook']
    >>> block = app.get_block('frmBook')

HTTP commands
    >>> from rapido.core.interfaces import IDisplay
    >>> display = IDisplay(app)
    >>> display.GET(['testapp', 'block', 'frmBook'], {})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/block/frmBook"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="" />\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.GET(['testapp', 'block', 'not_existing'], {})
    Traceback (most recent call last):
    ...
    NotFound
    >>> display.GET(['testapp', 'record', 'record_1'], {})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: JOSEPH CONRAD\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.GET(['testapp', 'record', 'record_1_not_existing'], {})
    Traceback (most recent call last):
    ...
    NotFound
    >>> display.GET(['testapp', 'refresh'], {})
    (u'Refreshed (author, id)', '')
    >>> display.GET(['testapp', 'bad_directive'], {})
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> display.POST(['testapp', 'block', 'frmBook'], {})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/block/frmBook"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="" />\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.POST(['testapp', 'block', 'not_existing'], {})
    Traceback (most recent call last):
    ...
    NotFound
    >>> result = display.POST(['testapp', 'block', 'frmBook'], {'action.do_something': True})
    >>> display.POST(['testapp', 'record', 'record_1'], {'_save': True, 'author': 'J. Conrad'})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: J. Conrad\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.POST(['testapp', 'record', 'record_1111'], {'_save': True, 'author': 'J. Conrad'})
    Traceback (most recent call last):
    ...
    NotFound
    >>> display.POST(['testapp', 'record', 'record_1'], {})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: J. Conrad\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.POST(['testapp', 'record', 'record_1'], {'_edit': True})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: <input type="text"\n        name="author" value="J. Conrad" />\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.POST(['testapp', 'bad_directive'], {})
    Traceback (most recent call last):
    ...
    NotAllowed

REST commands
    >>> from rapido.core.interfaces import IRest
    >>> rest = IRest(app)
    >>> rest.GET([], "")
    {'acl': {'roles': {'boss': ['marie.curie']}, 'rights': {'author': ['FamousDiscoverers'], 'editor': ['marie.curie'], 'reader': ['isaac.newton']}}}
    >>> rest.GET(['bad_directive'], "")
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.GET(['block', 'frmBook'], "")
    {'code': '', 'elements': {'forever': {'type': 'TEXT', 'mode': 'COMPUTED_ON_CREATION'}, 'publication': {'type': 'DATETIME'}, 'author': {'index_type': 'text', 'type': 'TEXT'}, 'famous_quote': {'type': 'TEXT', 'mode': 'COMPUTED_ON_SAVE'}, 'year': {'type': 'NUMBER'}, 'do_something': {'type': 'ACTION', 'label': 'Do'}, '_save': {'type': 'ACTION', 'label': 'Save'}}, 'layout': 'Author: {author}\n<footer>Powered by Rapido</footer>', 'target': 'ajax', 'title': 'Book', 'debug': True, 'id': 'frmBook'}
    >>> rest.GET(['block', 'not_existing'], {})
    {'elements': {}, 'id': 'not_existing', 'title': ''}
    >>> len(rest.GET(['records'], ""))
    5
    >>> rest.GET(['record'], "")
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.GET(['record', 'not_existing'], "")
    Traceback (most recent call last):
    ...
    NotFound
    >>> rest.GET(['record', 'record_1'], "")
    {'author': 'J. Conrad', 'title': 'Book', 'book_tile': 'Lord Jim', 'famous_quote': None, 'id': 'record_1', 'block': 'frmBook', '_save': True}
    >>> result1 = rest.POST([], '{"item1": "value1"}')
    >>> result1
    {'path': 'http://here/record/...', 'id': '...', 'success': 'created'}
    >>> rest.POST(['record', result1['id']], '{"item1": "new value"}')
    {'success': 'updated'}
    >>> rest.POST(['record', 'unknown'], '{"item1": "new value"}')
    Traceback (most recent call last):
    ...
    NotFound
    >>> rest.POST(['search'], '{"query": "author==\'J. Conrad\'"}')
    [{'path': 'http://here/record/record_1', 'id': 'record_1', 'items': {'author': 'J. Conrad', 'title': 'Book', 'book_tile': 'Lord Jim', 'famous_quote': None, 'id': 'record_1', 'block': 'frmBook', '_save': True}}]
    >>> rest.POST(['refresh'], '')
    {'success': 'refresh', 'indexes': ['author', u'id']}
    >>> rest.POST(['refresh'], '{"rebuild": true}')
    {'success': 'refresh', 'indexes': ['author', u'id']}
    >>> rest.POST(['record'], '')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.POST(['bad_directive'], '')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.DELETE(['everything'], "")
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.PUT(['bad_directive'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.PUT(['record'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.PUT(['record', 'record_1'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.PUT(['record', 'new_record'], '{"item1": "value1"}')
    {'path': 'http://here/record/new_record', 'id': 'new_record', 'success': 'created'}
    >>> rest.PATCH(['record'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.PATCH(['bad_directive'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.PATCH(['record', 'not_existing'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    NotFound
    >>> rest.PATCH(['record', 'record_1'], '{"item1": "value1"}')
    {'success': 'updated'}
    >>> rest.DELETE(['record'], "")
    Traceback (most recent call last):
    ...
    NotAllowed
    >>> rest.DELETE(['record', 'not_existing'], "")
    Traceback (most recent call last):
    ...
    NotFound
    >>> rest.DELETE(['record', result1['id']], "")
    {'success': 'deleted'}

Access rights
    >>> app.acl.roles()
    {'boss': ['marie.curie']}
    >>> app_obj.set_fake_user("nobody")
    >>> display.GET(['testapp', 'refresh'], {})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> display.POST(['testapp', 'record', 'record_1'], {})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> app.acl.has_access_right("reader")
    False
    >>> display.GET(['testapp', 'record', 'record_1'], {})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.GET(['records'], "")
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.GET(['record', 'record_1'], "")
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.POST(['search'], '{"query": "author==\'J. Conrad\'"}')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.POST(['refresh'], '')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.PUT(['record', 'other_record'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.PATCH(['record', 'record_1'], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.DELETE(['record', result1['id']], "")
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> app_obj.set_fake_user("isaac.newton")
    >>> app.acl.has_access_right("reader")
    True
    >>> display.GET(['testapp', 'record', 'record_1'], {})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: J. Conrad\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.POST(['testapp', 'block', 'frmBook'], {'_save': True, 'item2': 'value2'})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> display.POST(['testapp', 'record', 'record_1'], {'_edit': True})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> display.POST(['testapp', 'record', 'record_1'], {'_save': True, 'item2': 'value2'})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.POST([], '{"item1": "value1"}')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.POST(['record', 'record_1'], '{"item1": "new value"}')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> rest.POST(['records'], '[{"item1": "new value"}, {"item1": "other value"}]')
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> app_obj.set_fake_user("FamousDiscoverers")
    >>> app.acl.has_access_right("author")
    True
    >>> display.POST(['testapp', 'record', 'record_1'], {'_save': True, 'item2': 'value2'})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> display.POST(['testapp', 'record', 'record_1'], {'_delete': True})
    Traceback (most recent call last):
    ...
    Unauthorized
    >>> display.POST(['testapp', 'block', 'frmBook'], {'_save': True, 'item1': 'value1'})
    ('', 'http://here/record/...')
    >>> app_obj.set_fake_user("marie.curie")
    >>> app.acl.has_access_right("editor")
    True
    >>> app.acl.has_role("anything")
    False
    >>> app.acl.has_role("boss")
    True
    >>> display.POST(['testapp', 'record', 'record_1'], {'_save': True, 'item2': 'value2'})
    (u'<form\n    name="frmBook"\n    class="rapido-block rapido-target-ajax"\n    action="http://here/record/record_1"\n    rapido-settings=\'{"target": "ajax", "title": "Book", "debug": true, "app": {"url": "http://here"}, "id": "frmBook"}\'\n    method="POST">Author: J. Conrad\n<footer>Powered by Rapido</footer></form>\n', '')
    >>> display.POST(['testapp', 'record', 'record_1'], {'_delete': True})
    ('deleted', '')
    >>> rest.DELETE(['record', 'new_record'], "")
    {'success': 'deleted'}

Log messages
    >>> app.log("Hello")
    >>> app.messages[2]
    'Hello'

Refresh all
    >>> app.refresh()
    >>> len(app.records())
    5

Clear storage
    >>> app.clear_storage()
    >>> len(app.records())
    0

Bulk import
    >>> app_obj.set_fake_user("admin")
    >>> rest.POST(['records'], '[{"item1": "new value"}, {"item1": "other value"}]')
    {'total': 2, 'success': 'created'}
    >>> len(app.records())
    2
    >>> rest.DELETE(['records'], '')
    {'success': 'deleted'}
    >>> len(app.records())
    0