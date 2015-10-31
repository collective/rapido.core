from zope.interface import implements

from .interfaces import IAccessControlList

ACCESS_RIGHTS_PERMISSIONS = {
    'reader': [
        'view',
    ],
    'author': [
        'view',
        'create',
    ],
    'if-author': [
        'edit',
        'delete',
    ],
    'editor': [
        'view',
        'create',
        'edit',
        'delete',
    ],
    'manager': [
        'view',
        'create',
        'edit',
        'delete',
        'manage',
    ],
}


class AccessControlList:
    implements(IAccessControlList)

    def __init__(self, context):
        self.context = context
        self._current_user = self.context.context.current_user()
        self._is_manager = self.context.context.is_manager()
        self._current_user_groups = self.context.context.current_user_groups()
        if 'acl' not in self.context.settings:
            self.context.settings['acl'] = {
                'rights': {
                    'reader': [],
                    'author': [],
                    'editor': [],
                },
                'roles': {},
            }

    def allowed_as(self, access_right):
        return self.context.settings['acl']['rights'][access_right]

    def roles(self):
        return self.context.settings['acl']['roles']

    def current_user(self):
        return self._current_user

    def is_manager(self):
        return self._is_manager

    def current_user_groups(self):
        return self._current_user_groups

    def has_role(self, role_id):
        role = self.roles().get(role_id)
        if not role:
            return False
        if self.current_user() in role:
            return True
        if any([(group in role) for group in self.current_user_groups()]):
            return True
        return False

    def has_access_right(self, access_right):
        allowed = self.allowed_as(access_right)
        if '*' in allowed:
            return True
        if self.current_user() in allowed:
            return True
        elif set(self.current_user_groups()).intersection(allowed):
            return True
        else:
            return False

    def has_permission(self, permission, record=None):
        if self.is_manager():
            return True
        for access_right in self.context.settings['acl']['rights']:
            if self.has_access_right(access_right):
                if permission in ACCESS_RIGHTS_PERMISSIONS[access_right]:
                    return True
                if (access_right == 'author' and record
                and self.current_user() in record.get_item('_author', [])
                and permission in ACCESS_RIGHTS_PERMISSIONS['if-author']):
                    return True
        return False
