from zope.interface import implements, alsoProvides, implementer, Interface
from node.base import BaseNode
from node.ext.zodb import OOBTNode
from zope.annotation.interfaces import IAttributeAnnotatable
from rapido.core.interfaces import IDatabasable, IFormable

class SiteNode(OOBTNode):
    implements(IAttributeAnnotatable)

class SimpleDatabase(BaseNode):
    implements(IAttributeAnnotatable, IDatabasable)
    def __init__(self, uid, root):
        self.uid = uid
        self['root'] = root
        self.fake_user = 'admin'
        self.fake_groups = []

    @property
    def root(self):
        return self['root']

    @property
    def forms(self):
        return [el for el in self.values() if el.__class__.__name__=='SimpleForm']

    def current_user(self):
        return self.fake_user

    def set_fake_user(self, user):
        self.fake_user = user

    def current_user_groups(self):
        return self.fake_groups

    def set_fake_groups(self, groups):
        self.fake_groups = groups


class SimpleForm(BaseNode):
    implements(IAttributeAnnotatable, IFormable)
    def __init__(self, id, title):
        self.id = id
        self.title = title