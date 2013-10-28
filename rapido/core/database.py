from zope.interface import implements

from interfaces import IDatabase


class Database(object):
    """
    """
    implements(IDatabase)

    def __init__(self, context):
        self.context = context
        