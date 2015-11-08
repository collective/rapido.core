from zope.untrustedpython.interpreter import CompiledProgram
from zope.event import notify

from .events import ExecutionErrorEvent, CompilationErrorEvent


class Compiler(CompiledProgram):
    """ Compile the source code contained in the 'code' property.
    """
    def __init__(self, container):
        self.source = getattr(container, 'code', '')
        self.code = compile(
            self.source,
            "%s.py" % container.id,
            'exec')


class FormulaContainer(object):

    def compile(self):
        try:
            self._compiled_code = Compiler(self)
        except Exception, e:
            self._compiled_code = None
            self._executable = None
            notify(CompilationErrorEvent(e, self))
            return False
        self._executable = {}
        self._compiled_code.exec_(self._executable)
        return True

    def _execute(self, func, *args, **kwargs):
        if not hasattr(self, '_executable'):
            compiled = self.compile()
        else:
            compiled = True
        if compiled and self._executable and func in self._executable:
            try:
                return self._executable[func](*args, **kwargs)
            except Exception, e:
                notify(ExecutionErrorEvent(e, self))

    def execute(self, func, *args, **kwargs):
        return self._execute(func, *args, **kwargs)
