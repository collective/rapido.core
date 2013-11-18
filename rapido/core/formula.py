from zope.security.untrustedpython.interpreter import CompiledProgram
from zope.event import notify
from zope.annotation.interfaces import IAnnotations
import marshal

from .events import ExecutionErrorEvent, CompilationErrorEvent
from rapido.core import ANNOTATION_KEY


class PersistentCompiledProgram(CompiledProgram):

    def __init__(self, container, recompile=False):
        annotations = IAnnotations(container)
        if ANNOTATION_KEY not in annotations:
            annotations[ANNOTATION_KEY] = PersistentDict({
                'code': "",
                'compiled_code': "",
            })
        self.source = annotations[ANNOTATION_KEY]['code']
        compiled_code = annotations[ANNOTATION_KEY].get('compiled_code', None)
        if not recompile and compiled_code:
            self.code = marshal.loads(compiled_code)
        else:
            self.code = compile(
                self.source,
                "%s.py" % container.id,
                'exec')
            annotations[ANNOTATION_KEY]['compiled_code'] = marshal.dumps(self.code)


class FormulaContainer(object):

    def compile(self, recompile=False):
        try:
            self._compiled_code = PersistentCompiledProgram(self.context, recompile)
        except Exception, e:
            self._compiled_code = None
            self._executable = None
            notify(CompilationErrorEvent(e, self))
            return
        self._executable = {}
        self._compiled_code.exec_(self._executable)

    def execute(self, func, *args, **kwargs):
        if not hasattr(self, '_executable'):
            self.compile()
        if func in self._executable:
            try:
                return self._executable[func](*args, **kwargs)
            except Exception, e:
                notify(ExecutionErrorEvent(e, self))