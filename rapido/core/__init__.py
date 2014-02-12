from zope.security.checker import NamesChecker, defineChecker
from rapido.core.database import Database

defineChecker(Database, NamesChecker(['search']))
