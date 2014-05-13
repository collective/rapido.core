from zope.untrustedpython.interpreter import CompiledProgram
from zope.event import notify
from zope.annotation.interfaces import IAnnotations
import marshal

from .events import ExecutionErrorEvent, CompilationErrorEvent
from .database import ANNOTATION_KEY as KEY


class PersistentCompiledProgram(CompiledProgram):
    """ Store the compiled code in an annotation.
    The annotation must contain the source code in a dictionary entry named
    'code' or '<rule_id>_code'.
    """
    def __init__(self, container, recompile=False, prefix=None):
        code_id = 'code'
        if prefix:
            code_id = prefix + "_" + code_id
        annotations = IAnnotations(container)
        self.source = annotations[KEY].get(code_id, '')
        compiled_code = annotations[KEY].get('compiled_' + code_id, None)
        if not recompile and compiled_code:
            self.code = marshal.loads(compiled_code)
        else:
            self.code = compile(
                self.source,
                "%s.py" % container.id,
                'exec')
            annotations[KEY]['compiled_' + code_id] = marshal.dumps(self.code)


class FormulaContainer(object):

    def compile(self, recompile=False, prefix=''):
        compiled_code_id = '_%s_compiled_code' % prefix
        executable_id = '_%s_executable' % prefix
        try:
            setattr(self, compiled_code_id, PersistentCompiledProgram(
                self.context,
                recompile=recompile,
                prefix=prefix)
            )
        except Exception, e:
            setattr(self, compiled_code_id, None)
            setattr(self, executable_id, None)
            notify(CompilationErrorEvent(e, self))
            return
        setattr(self, executable_id, {})
        getattr(self, compiled_code_id).exec_(getattr(self, executable_id))

    def _execute(self, prefix, func, *args, **kwargs):
        executable_id = '_%s_executable' % prefix
        if not hasattr(self, executable_id):
            self.compile(prefix=prefix)
        if func in getattr(self, executable_id):
            try:
                return getattr(self, executable_id)[func](*args, **kwargs)
            except Exception, e:
                notify(ExecutionErrorEvent(e, self))

    def execute(self, func, *args, **kwargs):
        return self._execute('', func, *args, **kwargs)

    def execute_rule(self, rule_id, func, *args, **kwargs):
        return self._execute(rule_id, func, *args, **kwargs)