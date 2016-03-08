import logging
import traceback

logger = logging.getLogger("Rapido")


class NotAllowed(Exception):
    pass


class Unauthorized(Exception):
    pass


class NotFound(Exception):

    def __init__(self, name):
        self.name = name


class CompilationError(Exception):

    def __init__(self, error, container):
        self.message = """Rapido compilation error - %s
in %s.py, at line %d: %s
%s
%s""" % (
            container.app.context.id,
            container.id,
            error.lineno,
            error.msg,
            error.text.replace('\n', ''),
            '-' * (error.offset - 1) + '^',
        )
        logger.error(self.message)
        container.app.add_message(self.message)

    def __str__(self):
        msg = self.message.encode('utf-8')
        return msg


class ExecutionError(Exception):

    def __init__(self, error, container):
        trace = traceback.format_exc().splitlines()
        error_msg = trace[-1]
        error_line = trace[-2].replace('  File "<string>", ', '')
        self.message = """Rapido execution error - %s
%s
%s""" % (
            container.app.context.id,
            error_line,
            error_msg,
        )
        logger.error(self.message)
        container.app.add_message(self.message)

    def __str__(self):
        msg = self.message.encode('utf-8')
        return msg
