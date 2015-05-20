from zope.interface import implements

from .interfaces import IAccessControlList
from .exceptions import NotAllowed

ACCESS_RIGHTS_PERMISSIONS = {
    'reader': [
        'view',
    ],
    'author': [
        'view',
        'create_document',
        'edit_document',
        'delete_document',
    ],
    'editor': [
        'view',
        'create_document',
        'edit_document',
        'delete_document',
    ],
    'manager': [
        'view',
        'create_document',
        'edit_document',
        'delete_document',
        'modify_app',
        'modify_acl',
    ],
}


class acl_check:
    """" access control decorator
    """
    def __init__(self, permission):
        self.permission = permission

    def __call__(self, f):
        def newf(*args, **kwds):
            obj = args[0]
            acl = IAccessControlList(obj)
            if acl.has_permission(self.permission):
                return f(*args, **kwds)
            else:
                raise NotAllowed, "%s permission required" % self.permission

        newf.__doc__ = f.__doc__
        return newf


class AccessControlList:
    implements(IAccessControlList)

    def __init__(self, context):
        self.context = context
        if 'acl' not in self.context.annotation:
            self.context.annotation['acl'] = {
                'rights': {
                    'reader': [],
                    'author': [],
                    'editor': [],
                    'manager': [self.current_user()],
                    },
                'roles': {},
            }

    def allowed_as(self, access_right):
        return self.context.annotation['acl']['rights'][access_right]

    def roles(self):
        return self.context.annotation['acl']['roles']

    def current_user(self):
        return self.context.context.current_user()

    def current_user_groups(self):
        return self.context.context.current_user_groups()

    def has_access_right(self, access_right):
        allowed = self.allowed_as(access_right)
        if self.current_user() in allowed:
            return True
        elif set(self.current_user_groups()).intersection(allowed):
            return True
        else:
            return False

    def has_permission(self, permission):
        for access_right in self.context.annotation['acl']['rights']:
            if self.has_access_right(access_right):
                if permission in ACCESS_RIGHTS_PERMISSIONS[access_right]:
                    return True
        return False

    @acl_check('modify_acl')
    def grant_access(self, users_or_groups, access_right):
        self.context.annotation['acl']['rights'][access_right] = users_or_groups