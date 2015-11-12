from zope.component.interfaces import ObjectEvent
from zope.interface import Interface, implements
import traceback


class ICompilationErrorEvent(Interface):
    """ when user code cannot be compiled """
    pass


class CompilationErrorEvent(ObjectEvent):
    implements(ICompilationErrorEvent)

    def __init__(self, provider, container):
        super(CompilationErrorEvent, self).__init__(provider)
        self.error = provider
        self.container = container
        self.message = """in %s, at line %d: %s""" % (
            container.id,
            self.error.lineno,
            self.error.msg,
        )


class IExecutionErrorEvent(Interface):
    """ when user code fails """
    pass


class ExecutionErrorEvent(ObjectEvent):
    implements(IExecutionErrorEvent)

    def __init__(self, provider, container):
        super(ExecutionErrorEvent, self).__init__(provider)
        self.error = provider
        self.container = container
        self.traceback = traceback.format_exc().splitlines()

        error_msg = getattr(self.error, 'message', "%s %s" % (
            self.error.__class__.__name__,
            str(self.error)))
        error_line = self.traceback[-2].replace('  File "<string>", ', '')
        self.message = """%s, %s""" % (
            error_msg,
            error_line,
        )
