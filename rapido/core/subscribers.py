import logging

logger = logging.getLogger("Rapido")

def on_compilation_error(event):
    message = """in %s, at line %d: %s
%s
%s""" % (
        event.container.id,
        event.error.lineno,
        event.error.msg,
        event.error.text.replace('\n', ''),
        '-'*(event.error.offset-1)+'^',
    )
    logger.error(message)

def on_execution_error(event):
    message = """in %s: %s""" % (
        event.container.id,
        event.error.message,
    )
    logger.error(message)