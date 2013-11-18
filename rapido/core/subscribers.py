import logging

logger = logging.getLogger("Rapido")

def on_compilation_error(event):
    message = """%s
%s
%s""" % (
        event.message,
        event.error.text.replace('\n', ''),
        '-'*(event.error.offset-1)+'^',
    )
    logger.error(message)

def on_execution_error(event):
    logger.error(event.message)
