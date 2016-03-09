from datetime import datetime
import unittest
import zope.annotation
import zope.browserpage
import zope.component
from zope.configuration.xmlconfig import XMLConfig
from zope.publisher.browser import TestRequest

import rapido.core
import rapido.souper
from rapido.core.interfaces import IRapidoApplication
import rapido.core.tests
from rapido.core.tests.base import SiteNode, SimpleRapidoApplication


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

    def test_create_record(self):
        record = self.app.create_record(id='record_1')
        self.assertEquals(record.id, 'record_1')

    def test_record_items(self):
        record = self.app.create_record(id='record_1')
        record['author'] = "Joseph Conrad"
        record['book_tile'] = "Lord Jim"
        self.assertEquals(record['author'], 'Joseph Conrad')
        record['not_important'] = 2
        self.assertTrue('not_important' in record)
        del record['not_important']
        self.assertEquals(
            [key for key in record],
            ['book_tile', 'id', 'author']
        )

    def test_find_by_uid(self):
        record = self.app.create_record(id='record_1')
        uid = record.uid
        self.assertEquals(
            self.app.get_record(uid).uid,
            self.app.get_record('record_1').uid
        )

    def test_unique_id(self):
        self.app.create_record(id='record_1')
        record_bis = self.app.create_record(id='record_1')
        self.assertTrue(record_bis.id != 'record_1')
        self.assertTrue(record_bis.id.startswith('record_1-'))

    def test_search(self):
        record = self.app.create_record(id='record_1')
        # by calling the block we make sure indexes are built
        self.app.get_block('frmBook')
        record['author'] = "Joseph Conrad"
        record.reindex()
        self.assertEquals(
            [rec['author'] for rec in self.app.search('id=="record_1"')],
            ['Joseph Conrad']
        )
        self.assertEquals(
            [rec['author']
                for rec in self.app.search('author=="Joseph Conrad"')],
            ['Joseph Conrad']
        )
        self.assertEquals(
            [rec['author'] for rec in self.app.search('"joseph" in author')],
            ['Joseph Conrad']
        )

    def test_delete(self):
        record = self.app.create_record()
        the_id = record.id
        self.app.delete_record(record=record)
        self.assertTrue(self.app.get_record(the_id) is None)
        record2 = self.app.create_record()
        the_id = record2.id
        self.app.delete_record(id=the_id)
        self.assertTrue(self.app.get_record(the_id) is None)

    def test_save_from_dict(self):
        record = self.app.create_record()
        record.save({'author': "John DosPassos"})
        self.assertEquals(record['author'], "John DosPassos")

    def test_save_from_request(self):
        record = self.app.create_record()
        request = TestRequest()
        self.assertRaises(
            Exception,
            record.save,
            request
        )
        request = TestRequest(form=dict(
            block='frmBook',
            author='J. DosPassos',
            year='2015',
            publication='2015-11-15',
            weight='1.3',
        ))
        record.save(request)
        self.assertEquals(record['author'], "J. DOSPASSOS")
        self.assertEquals(record['year'], 2015)
        self.assertEquals(record['weight'], 1.3)
        self.assertEquals(
            record['publication'],
            datetime.strptime('2015-11-15', "%Y-%m-%d")
        )

    def test_compute_element_on_save(self):
        record = self.app.create_record()
        record.save(block_id="frmBook")
        self.assertEquals(
            record['famous_quote'],
            'A good plan violently executed now is better than a perfect plan '
            'executed next week.'
        )

    def test_render_number_elements(self):
        self.app_obj.set_fake_block_data('frmBook', 'html', """Author: {author}
 {year} {weight}<footer>Powered by Rapido</footer>""")
        if 'frmBook' in self.app._blocks:
            del self.app._blocks['frmBook']
        block = self.app.get_block('frmBook')
        record = self.app.create_record()
        record.save({
            'year': 1845,
            'weight': 3.2,
        })
        html = block.display(record, edit=True)
        self.assertTrue('<input type="number"\n'
            '        name="year" value="1845" />' in html)
        self.assertTrue('<input type="number"\n'
            '        name="weight" value="3.2" />' in html)

    def test_render_datetime_elements(self):
        self.app_obj.set_fake_block_data('frmBook', 'html', """Author: {author}
 {publication}<footer>Powered by Rapido</footer>""")
        if 'frmBook' in self.app._blocks:
            del self.app._blocks['frmBook']
        block = self.app.get_block('frmBook')
        html = block.display(None, edit=True)
        self.assertTrue('<input type="date"\n'
            '        name="publication" value="" />' in html)
        record = self.app.create_record()
        record.save({
            'publication': datetime.strptime('2015-11-15', "%Y-%m-%d"),
        })
        html = block.display(record, edit=True)
        self.assertTrue('<input type="date"\n'
            '        name="publication" value="2015-11-15" />' in html)

    def test_compute_element_using_record_data(self):
        block = self.app.get_block('frmBook7')
        record = self.app.create_record()
        record.save({
            'author': 'John DosPassos',
        })
        html = block.display(record, edit=True)
        self.assertTrue('Bonjour John DosPassos' in html)
