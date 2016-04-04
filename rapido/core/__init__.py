import datetime
import random
import time

from zope.security.checker import NamesChecker
from zope.security.checker import defineChecker

from rapido.core.app import RapidoApplication


defineChecker(RapidoApplication, NamesChecker(['search']))

safe_modules = [datetime, random, time]
for module in safe_modules:
    defineChecker(
        module,
        NamesChecker([meth for meth in dir(module) if meth[0] != '_'])
    )
