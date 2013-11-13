from zope.component.interfaces import ObjectEvent
from zope.interface import Interface,implements


class ICompilationErrorEvent(Interface):
    """ when user code cannot be compiled """
    pass


class CompilationErrorEvent(ObjectEvent):
    implements(ICompilationErrorEvent)

    def __init__(self, provider, container):
        super(CompilationErrorEvent, self).__init__(provider)
        self.error = provider
        self.container = container


class IExecutionErrorEvent(Interface):
    """ when user code fails """
    pass


class ExecutionErrorEvent(ObjectEvent):
    implements(IExecutionErrorEvent)

    def __init__(self, provider, container):
        super(ExecutionErrorEvent, self).__init__(provider)
        self.error = provider
        self.container = container
    
