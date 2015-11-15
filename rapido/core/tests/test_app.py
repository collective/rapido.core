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
    reader: [FamousDiscoverers]
  roles: {"boss": ["marie.curie"], "biology": ["FamousDiscoverers"]}"""
        self.app = IRapidoApplication(self.app_obj)
        self.app.initialize()

    def test_settings(self):
        self.assertEquals(
            self.app.settings,
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
                        'reader': ['FamousDiscoverers']
                    }
                }
            }
        )

    def test_default_settings(self):
        self.app_obj.settings = 'no_settings: {}'
        self.app = IRapidoApplication(self.app_obj)
        self.app.initialize()
        self.assertEquals(
            self.app.settings,
            {
                'no_settings': {},
                'acl': {
                    'roles': {},
                    'rights': {
                        'author': [],
                        'editor': [],
                        'reader': []
                    }
                }
            }
        )

    def test_acl(self):
        self.assertEquals(
            self.app.acl.roles(),
            {'biology': ['FamousDiscoverers'], 'boss': ['marie.curie']}
        )

    def test_access_rights(self):
        self.app_obj.set_fake_user("marie.curie")
        self.assertTrue(self.app.acl.has_access_right('editor'))
        self.app_obj.set_fake_user("anybody")
        self.assertFalse(self.app.acl.has_access_right('reader'))
        self.app_obj.set_fake_groups(["FamousDiscoverers"])
        self.assertTrue(self.app.acl.has_access_right('reader'))

    def test_roles(self):
        self.app_obj.set_fake_user("marie.curie")
        self.assertTrue(self.app.acl.has_role('boss'))
        self.app_obj.set_fake_user("isaac.newton")
        self.assertFalse(self.app.acl.has_role('boss'))
        self.assertFalse(self.app.acl.has_role('not_a_role'))
        self.app_obj.set_fake_groups(["FamousDiscoverers"])
        self.assertTrue(self.app.acl.has_role('biology'))
