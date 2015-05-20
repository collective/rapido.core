from zope.security.checker import NamesChecker, defineChecker
from rapido.core.app import RapidoApplication

defineChecker(RapidoApplication, NamesChecker(['search']))
