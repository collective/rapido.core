from zope.security.checker import NamesChecker, defineChecker
from rapido.core.database import Database

defineChecker(Database, NamesChecker(['search']))

ANNOTATION_KEY = "RAPIDO_ANNOTATION"