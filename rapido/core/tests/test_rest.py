import unittest
import zope.annotation
import zope.browserpage
import zope.component
from zope.configuration.xmlconfig import XMLConfig

import rapido.core
from rapido.core.interfaces import IRapidoApplication, IRest
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

    def test_get_app(self):
        rest = IRest(self.app)
        result = rest.GET([], "")
        self.assertEquals(result,
            {
                'debug': True,
                'acl': {
                    'roles': {
                        'biology': ['FamousDiscoverers'],
                        'boss': ['marie.curie']
                    },
                    'rights': {
                        'author': ['isaac.newton'],
                        'editor': ['marie.curie'],
                        'reader': []
                    }
                }
            })

    def test_get_bad_directive(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.GET,
            ['bad_directive'],
            ""
        )

    def test_get_block(self):
        rest = IRest(self.app)
        result = rest.GET(['blocks', 'frmBook2'], "")
        self.assertEquals(result,
            {
                'elements': {
                    'do_something': {
                        'type': 'ACTION',
                        'label': 'Do'
                    },
                    'author': {'type': 'TEXT'}
                },
                'target': 'ajax'
            }
        )

    def test_get_element(self):
        rest = IRest(self.app)
        result = rest.GET(['blocks', 'frmBook', 'something_computed'], "")
        self.assertEquals(result,
            {'one': 1, 'two': 2.0}
        )

    def test_post_element(self):
        rest = IRest(self.app)
        result = rest.POST(['blocks', 'frmBook', 'something_computed'], "")
        self.assertEquals(result,
            {'one': 1, 'two': 2.0}
        )

    def test_post_without_element(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.POST,
            ['blocks', 'frmBook'],
            ""
        )

    def test_get_block_too_many_param(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.GET,
            ['blocks', 'frmBook', 'what', 'ever'],
            ""
        )

    def test_get_not_defined_block(self):
        rest = IRest(self.app)
        result = rest.GET(['blocks', 'anything'], "")
        self.assertEquals(result,
            {'elements': {}, 'id': 'anything'}
        )

    def test_get_records(self):
        self.app.create_record(id='record_1')
        self.app.create_record(id='record_2')
        rest = IRest(self.app)
        self.assertEquals(len(rest.GET(['records'], "")), 2)

    def test_get_records_not_reader(self):
        self.app.create_record(id='record_1')
        self.app.create_record(id='record_2')
        rest = IRest(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            rest.GET,
            ['records'],
            ""
        )

    def test_get_record_without_param(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.GET,
            ['record'],
            ""
        )

    def test_get_not_existing_record(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotFound,
            rest.GET,
            ['record', 'not_existing'],
            ""
        )

    def test_get_record(self):
        record = self.app.create_record(id='record_1')
        record.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        self.app.settings['acl']['rights']['reader'] = ['*']
        self.app_obj.set_fake_user("anybody")
        self.assertTrue(self.app.acl.has_access_right("reader"))
        rest = IRest(self.app)
        result = rest.GET(['record', 'record_1'], "")
        self.assertEquals(
            result,
            {
                'forever': 'I will never change.',
                'famous_quote': 'A good plan violently executed now is '
                'better than a perfect plan executed next week.',
                'id': 'record_1',
                'block': 'frmBook',
                'author': 'JOHN DOSPASSOS'
            }
        )

    def test_get_record_not_reader(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            rest.GET,
            ['record', 'record_1'],
            ""
        )

    def test_post_new_record(self):
        rest = IRest(self.app)
        result = rest.POST([], '{"item1": "value1"}')
        self.assertEquals(result['success'], 'created')
        self.assertIn('path', result)
        self.assertIn('id', result)

    def test_post_new_record_not_author(self):
        self.app_obj.set_fake_user("anybody")
        self.assertFalse(self.app.acl.has_access_right("author"))
        rest = IRest(self.app)
        self.assertRaises(
            Unauthorized,
            rest.POST,
            [],
            '{"item1": "value1"}'
        )

    def test_post_existing_record(self):
        record = self.app.create_record(id='record_1')
        rest = IRest(self.app)
        result = rest.POST(['record', 'record_1'], '{"item1": "value1"}')
        self.assertEquals(result, {'success': 'updated'})
        self.assertEquals(record['item1'], 'value1')

    def test_post_existing_record_not_author(self):
        self.app.create_record(id='record_1')
        self.app_obj.set_fake_user("anybody")
        rest = IRest(self.app)
        self.assertRaises(
            Unauthorized,
            rest.POST,
            ['record', 'record_1'],
            '{"item1": "value1"}'
        )

    def test_post_not_existing_record(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotFound,
            rest.POST,
            ['record', 'not_existing'],
            '{"item1": "value1"}'
        )

    def test_post_bulk(self):
        rest = IRest(self.app)
        result = rest.POST(['records'],
            '[{"item1": "new value"}, {"item1": "other value"}]')
        self.assertEquals(result, {'total': 2, 'success': 'created'})
        self.assertEquals(len(self.app.records()), 2)

    def test_post_bulk_not_author(self):
        self.app_obj.set_fake_user("anybody")
        rest = IRest(self.app)
        self.assertRaises(
            Unauthorized,
            rest.POST,
            ['records'],
            '[{"item1": "new value"}, {"item1": "other value"}]'
        )

    def test_search(self):
        record_1 = self.app.create_record(id='record_1')
        record_1.save(
            {'author': "John DosPassos"},
            block_id="frmBook",
            creation=True)
        record_2 = self.app.create_record(id='record_2')
        record_2.save(
            {'author': "J. Conrad"},
            block_id="frmBook",
            creation=True)
        rest = IRest(self.app)
        result = rest.POST(['search'], '{"query": "author==\'J. CONRAD\'"}')
        self.assertEquals(len(result), 1)

    def test_search_not_reader(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        self.app_obj.set_fake_user("nobody")
        self.assertRaises(
            Unauthorized,
            rest.POST,
            ['search'],
            '{"query": "author==\'J. CONRAD\'"}'
        )

    def test_refresh(self):
        rest = IRest(self.app)
        result = rest.POST(['refresh'], '')
        self.assertEquals(result,
            {'success': 'refresh', 'indexes': ['author', u'id']}
        )

    def test_refresh_with_rebuild(self):
        rest = IRest(self.app)
        result = rest.POST(['refresh'], '{"rebuild": true}')
        self.assertEquals(result,
            {'success': 'refresh', 'indexes': ['author', u'id']}
        )

    def test_refresh_not_reader(self):
        rest = IRest(self.app)
        self.app_obj.set_fake_user("marie.curie")
        self.assertRaises(
            Unauthorized,
            rest.POST,
            ['refresh'],
            ''
        )

    def test_post_record_without_param(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.POST,
            ['record'],
            ""
        )

    def test_post_bad_directive(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.POST,
            ['bad_directive'],
            ""
        )

    def test_delete_bad_param(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.DELETE,
            ['whatever'],
            ""
        )

    def test_delete_record_no_id(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.DELETE,
            ['record'],
            ""
        )

    def test_delete_record(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        result = rest.DELETE(['record', 'record_1'], "")
        self.assertEquals(result,
            {'success': 'deleted'}
        )
        self.assertEquals(len(self.app.records()), 0)

    def test_delete_record_not_author(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        self.app_obj.set_fake_user("anybody")
        self.assertRaises(
            Unauthorized,
            rest.DELETE,
            ['record', 'record_1'],
            ''
        )

    def test_delete_not_existing_record(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotFound,
            rest.DELETE,
            ['record', 'not_existing'],
            ""
        )

    def test_delete_all_records(self):
        self.app.create_record(id='record_1')
        self.app.create_record(id='record_2')
        rest = IRest(self.app)
        result = rest.DELETE(['records'], "")
        self.assertEquals(result,
            {'success': 'deleted'}
        )
        self.assertEquals(len(self.app.records()), 0)

    def test_delete_all_records_not_editor(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        self.app_obj.set_fake_user("isaac.newton")
        self.assertRaises(
            Unauthorized,
            rest.DELETE,
            ['records'],
            ''
        )

    def test_put_bad_directive(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.PUT,
            ['bad_directive'],
            '{"item1": "value1"}'
        )

    def test_put_new_record(self):
        rest = IRest(self.app)
        result = rest.PUT(['record', 'record_1'], '{"item1": "value1"}')
        self.assertEquals(result['success'], 'created')

    def test_put_new_record_not_author(self):
        rest = IRest(self.app)
        self.app_obj.set_fake_user("anybody")
        self.assertRaises(
            Unauthorized,
            rest.PUT,
            ['record', 'record_1'],
            '{"item1": "value1"}'
        )

    def test_put_existing_record(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.PUT,
            ['record', 'record_1'],
            '{"item1": "value1"}'
        )

    def test_put_without_id(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.PUT,
            ['record'],
            '{"item1": "value1"}'
        )

    def test_patch_record(self):
        record = self.app.create_record(id='record_1')
        rest = IRest(self.app)
        result = rest.PATCH(['record', 'record_1'], '{"item1": "value1"}')
        self.assertEquals(result,
            {'success': 'updated'}
        )
        self.assertEquals(record['item1'], 'value1')

    def test_patch_record_not_author(self):
        self.app.create_record(id='record_1')
        rest = IRest(self.app)
        self.app_obj.set_fake_user("anybody")
        self.assertRaises(
            Unauthorized,
            rest.PATCH,
            ['record', 'record_1'],
            '{"item1": "value1"}'
        )

    def test_patch_without_id(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.PATCH,
            ['record'],
            '{"item1": "value1"}'
        )

    def test_patch_bad_directive(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.PATCH,
            ['bad_directive'],
            '{"item1": "value1"}'
        )

    def test_patch_record_without_param(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotAllowed,
            rest.PATCH,
            ['record'],
            ""
        )

    def test_patch_not_existing_record(self):
        rest = IRest(self.app)
        self.assertRaises(
            NotFound,
            rest.PATCH,
            ['record', 'not_existing'],
            ""
        )
