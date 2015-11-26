import unittest
import zope.annotation
import zope.browserpage
import zope.component
from zope.configuration.xmlconfig import XMLConfig

import rapido.core
from rapido.core.interfaces import IRapidoApplication, IDisplay
from rapido.core.exceptions import NotFound, NotAllowed, Unauthorized
import rapido.core.tests
from rapido.core.tests.base import SiteNode, SimpleRapidoApplication
import rapido.souper


class TestCase(unittest.TestCase):

    def setUp(self):
        XMLConfig("meta.zcml", zope.component)()
        XMLConfig("meta.zcml", zope.browserpage)()
        XMLConfig("configure.zcml", zope.annotation)()
        XMLConfig("configure.zcml", rapido.core)()
        XMLConfig("configure.zcml", rapido.souper)()
        XMLConfig("configure.zcml", rapido.core.tests)()
        root = SiteNode()
        root['myapp'] = SimpleRapidoApplication("testapp", root)
        self.app_obj = root['myapp']
        self.app_obj.settings = """debug: true
acl:
  rights:
    author: [isaac.newton]
    editor: [marie.curie]
    reader: []
  roles: {"boss": ["marie.curie"], "biology": ["FamousDiscoverers"]}"""
        self.app = IRapidoApplication(self.app_obj)
        self.app.initialize()

    def test_get_block(self):
        display = IDisplay(self.app)
        result = display.GET(['testapp', 'block', 'frmBook'], {})
        self.assertEquals(result,
            (u'<form\n    name="frmBook"\n    class="rapido-block '
            'rapido-target-ajax"\n    action="http://here/block/frmBook"\n'
            '    rapido-settings=\'{"app": {"url": "http://here", '
            '"debug": true}, "target": "ajax", "id": "frmBook"}\'\n'
            '    method="POST">Author: <input type="text"\n'
            '        name="author" value="Victor Hugo" />\n<footer>'
            'Powered by Rapido</footer></form>\n', '')
        )

    def test_get_not_existing_block(self):
        display = IDisplay(self.app)
        self.assertRaises(
            NotFound,
            display.GET,
            ['testapp', 'block', 'not_existing'],
            {}
        )

    def test_get_record(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        display = IDisplay(self.app)
        result = display.GET(['testapp', 'record', 'record_1'], {})
        self.assertTrue('Author: JOHN DOSPASSOS' in result[0])

    def test_get_record_not_reader(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        self.app_obj.set_fake_user("nobody")
        self.assertFalse(self.app.acl.has_access_right("reader"))
        display = IDisplay(self.app)
        self.assertRaises(
            Unauthorized,
            display.GET,
            ['testapp', 'record', 'record_1'],
            {}
        )

    def test_get_record_edit(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        display = IDisplay(self.app)
        result = display.GET(['testapp', 'record', 'record_1', 'edit'], {})
        self.assertTrue('Author: <input type="text"\n'
        '        name="author" value="JOHN DOSPASSOS" />' in result[0])

    def test_get_not_existing_record(self):
        display = IDisplay(self.app)
        self.assertRaises(
            NotFound,
            display.GET,
            ['testapp', 'record', 'record_1_not_existing'],
            {}
        )

    def test_refresh(self):
        display = IDisplay(self.app)
        result = display.GET(['testapp', 'refresh'], {})
        self.assertEquals(result,
            (u'Refreshed (author, id)', ''))

    def test_refresh_not_manager(self):
        display = IDisplay(self.app)
        self.app_obj.set_fake_user("marie.curie")
        self.assertRaises(
            Unauthorized,
            display.GET,
            ['testapp', 'refresh'],
            {}
        )

    def test_get_bad_directive(self):
        display = IDisplay(self.app)
        self.assertRaises(
            NotAllowed,
            display.GET,
            ['testapp', 'bad_directive'],
            {}
        )

    def test_post_block(self):
        display = IDisplay(self.app)
        result = display.POST(['testapp', 'block', 'frmBook'], {})
        self.assertTrue('Author: <input type="text"\n'
        '        name="author" value="Victor Hugo" />' in result[0])

    def test_post_not_existing_block(self):
        display = IDisplay(self.app)
        self.assertRaises(
            NotFound,
            display.POST,
            ['testapp', 'block', 'not_existing'],
            {}
        )

    def test_post_block_action(self):
        display = IDisplay(self.app)
        display.POST([
            'testapp', 'block', 'frmBook2'],
            {'action.do_something': True})
        self.assertEquals(
            self.app.messages[-1],
            'Hello'
        )

    def test_post_block_save(self):
        display = IDisplay(self.app)
        display.POST([
            'testapp', 'block', 'frmBook2'],
            {'_save': True, 'author': 'J. Conrad'})
        self.assertEquals(
            len(self.app.records()),
            1
        )

    def test_post_block_save_not_author(self):
        display = IDisplay(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            display.POST,
            ['testapp', 'block', 'frmBook2'],
            {'_save': True, 'author': 'J. Conrad'}
        )

    def test_post_record(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        display = IDisplay(self.app)
        html = display.POST(
            ['testapp', 'record', 'record_1'],
            {})
        self.assertTrue('JOHN DOSPASSOS' in html[0])

    def test_post_record_not_reader(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        display = IDisplay(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            display.POST,
            ['testapp', 'record', 'record_1'],
            {}
        )

    def test_post_record_save_editor(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        self.app_obj.set_fake_user("marie.curie")
        display = IDisplay(self.app)
        display.POST(
            ['testapp', 'record', 'record_1'],
            {'_save': True, 'author': 'J. Conrad'})
        self.assertEquals(record['author'], 'J. Conrad')

    def test_post_record_save_author(self):
        self.app_obj.set_fake_user("isaac.newton")
        display = IDisplay(self.app)
        display.POST([
            'testapp', 'block', 'frmBook2'],
            {'_save': True, 'author': 'John DosPassos'})
        record = self.app.records()[0]
        self.assertEquals(record['_author'], ['isaac.newton'])
        display.POST(
            ['testapp', 'record', record.id],
            {'_save': True, 'author': 'J. Conrad'})
        self.assertEquals(record['author'], 'J. Conrad')

    def test_post_record_save_not_author(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        self.assertTrue('_author' not in record)
        display = IDisplay(self.app)
        self.app_obj.set_fake_user("isaac.newton")
        self.assertRaises(
            Unauthorized,
            display.POST,
            ['testapp', 'record', 'record_1'],
            {'_save': True, 'author': 'J. Conrad'}
        )

    def test_post_not_existing_record(self):
        display = IDisplay(self.app)
        self.assertRaises(
            NotFound,
            display.POST,
            ['testapp', 'record', 'record_not_existing'],
            {'_save': True, 'author': 'J. Conrad'}
        )

    def test_post_record_edit_action(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        display = IDisplay(self.app)
        result = display.POST(
            ['testapp', 'record', 'record_1'],
            {'_edit': True})
        self.assertTrue('Author: <input type="text"\n'
        '        name="author" value="JOHN DOSPASSOS" />' in result[0])

    def test_post_record_edit_not_author(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        display = IDisplay(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            display.POST,
            ['testapp', 'record', 'record_1'],
            {'_edit': True}
        )

    def test_post_record_action(self):
        record = self.app.create_record(id='record_1')
        record.set_block("frmBook")
        display = IDisplay(self.app)
        display.POST(
            ['testapp', 'record', 'record_1'],
            {'action.add_note': True})
        self.assertEquals(
            record['note'],
            "That's a good book"
        )

    def test_post_bad_directive(self):
        display = IDisplay(self.app)
        self.assertRaises(
            NotAllowed,
            display.POST,
            ['testapp', 'bad_directive'],
            {}
        )

    def test_delete_record(self):
        self.app.create_record(id='record_1')
        display = IDisplay(self.app)
        display.POST(
            ['testapp', 'record', 'record_1'],
            {'_delete': True})
        self.assertEquals(len(self.app.records()), 0)

    def test_delete_record_not_author(self):
        self.app.create_record(id='record_1')
        display = IDisplay(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            display.POST,
            ['testapp', 'record', 'record_1'],
            {'_delete': True}
        )
