import unittest
import zope.annotation
import zope.browserpage
import zope.component
from zope.configuration.xmlconfig import XMLConfig

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

    def test_no_code(self):
        block = self.app.get_block('frmBook3')
        self.assertEquals(block.code, '# no code')

    def test_display(self):
        block = self.app.get_block('frmBook')
        self.assertEquals(
            block.display(None, edit=True),
            u'<form\n    name="frmBook"\n    class="rapido-block '
            'rapido-target-ajax"\n    action="http://here/block/frmBook"\n'
            '    rapido-settings=\'{"app": {"url": "http://here", '
            '"debug": true}, "target": "ajax", "id": "frmBook"}\'\n'
            '    method="POST">Author: <input type="text"\n'
            '        name="author" value="Victor Hugo" />\n<footer>'
            'Powered by Rapido</footer></form>\n'
        )

    def test_display_record(self):
        block = self.app.get_block('frmBook')
        record = self.app.create_record(id='record_1')
        record['author'] = "Joseph Conrad"
        self.assertEquals(
            block.display(record),
            u'<form\n    name="frmBook"\n    class="rapido-block '
            'rapido-target-ajax"\n    action="http://here/record/record_1"\n'
            '    rapido-settings=\'{"app": {"url": "http://here", '
            '"debug": true}, "target": "ajax", "id": "frmBook"}\'\n'
            '    method="POST">Author: Joseph Conrad\n<footer>'
            'Powered by Rapido</footer></form>\n'
        )
        self.assertTrue(
            u"""<input type="text"
        name="author" value="Joseph Conrad" />""" in block.display(
                record, edit=True))

    def test_on_save(self):
        block = self.app.get_block('frmBook')
        record = self.app.create_record(id='record_1')
        record['author'] = "Joseph Conrad"
        record.save(block=block)
        self.assertEquals(
            record['author'],
            'JOSEPH CONRAD'
        )

    def test_on_delete(self):
        record_1 = self.app.create_record(id='record_1')
        record_2 = self.app.create_record(id='record_2')
        record_2.set_block('frmBook2')
        self.app.delete_record(record=record_2)
        self.assertEquals(
            record_1['message'],
            'Good bye'
        )

    def test_compute_id(self):
        block = self.app.get_block('frmBook2')
        record2 = self.app.create_record()
        record2.save({'author': "John DosPassos"}, block=block, creation=True)
        self.assertEquals(record2.id, 'my-id')
        record3 = self.app.create_record()
        record3.save(
            {'author': "John DosPassos"},
            block_id="frmBook2",
            creation=True)
        self.assertTrue(record3.id.startswith('my-id-'))

    def test_python_compilation_errors(self):
        block = self.app.get_block('frmBook4')
        block.display(None, edit=True)
        self.assertEquals(
            self.app.messages[0],
            "Rapido compilation error - testapp:\nin frmBook4, at line 3: "
            "invalid syntax\n    returm 'hello'\n-----------------^"
        )
        self.app_obj.set_fake_block_data('frmBook4', 'py', """
def author(context):
    return context.not_a_method()""")
        del self.app._blocks['frmBook4']
        block = self.app.get_block('frmBook4')
        block.display(None, edit=True)
        self.assertEquals(
            self.app.messages[1],
            'Rapido execution error - testapp:\n   \'Context\' object has no '
            'attribute \'not_a_method\'\n   File "frmBook4.py", line 3, in '
            'author'
        )

    def test_undefined_element(self):
        self.app_obj.set_fake_block_data('frmBook2', 'html', """Author: {author}
{summary}<footer>Powered by Rapido</footer>""")
        if 'frmBook2' in self.app._blocks:
            del self.app._blocks['frmBook2']
        block = self.app.get_block('frmBook2')
        self.assertTrue(u'UNDEFINED ELEMENT' in block.display(None, edit=True))

    def test_undefined_element_type(self):
        block = self.app.get_block('frmBook5')
        self.assertTrue(u'UNKNOWN ELEMENT TYPE' in block.display(
            None, edit=True))

    def test_render_action(self):
        self.app_obj.set_fake_block_data('frmBook2', 'html', """Author: {author}
 {do_something} {_save}<footer>Powered by Rapido</footer>""")
        if 'frmBook2' in self.app._blocks:
            del self.app._blocks['frmBook2']
        block = self.app.get_block('frmBook2')
        html = block.display(None, edit=True)
        self.assertTrue('<input type="submit"\n'
            '        name="action.do_something" value="Do" />' in html)

    def test_render_special_action(self):
        block = self.app.get_block('frmBook5')
        html = block.display(None, edit=True)
        self.assertTrue('<input type="submit"\n'
            '        name="_save" value="Save" />' in html)

    def test_python_not_mandatory(self):
        block = self.app.get_block('frmBook3')
        self.assertTrue(
            u'Author: <input type="text"\n'
            '        name="author" value="" />' in block.display(
                None, edit=True)
        )
