from zope.untrustedpython.interpreter import CompiledProgram
from zope.event import notify
import marshal

from .events import ExecutionErrorEvent, CompilationErrorEvent


class PersistentCompiledProgram(CompiledProgram):
    """ Store the compiled code in an annotation.
    The annotation must contain the source code in a dictionary entry named
    'code' or '<rule_id>_code'.
    """
    def __init__(self, container, recompile=False):
        self.source = getattr(container, 'code', '')
        compiled_code = getattr(container, 'compiled_code', None)
        if not recompile and compiled_code:
            self.code = marshal.loads(compiled_code)
        else:
            self.code = compile(
                self.source,
                "%s.py" % container.id,
                'exec')
            container.compiled_code = marshal.dumps(self.code)


class FormulaContainer(object):

    def compile(self, recompile=False):
        try:
            self._compiled_code = PersistentCompiledProgram(
                self,
                recompile=recompile)
        except Exception, e:
            self._compiled_code = None
            self._executable = None
            notify(CompilationErrorEvent(e, self))
            return
        self._executable = {}
        self._compiled_code.exec_(self._executable)

    def _execute(self, func, *args, **kwargs):
        if not hasattr(self, '_executable'):
            self.compile()
        if func in self._executable:
            try:
                return self._executable[func](*args, **kwargs)
            except Exception, e:
                notify(ExecutionErrorEvent(e, self))

    def execute(self, func, *args, **kwargs):
        return self._execute(func, *args, **kwargs)
