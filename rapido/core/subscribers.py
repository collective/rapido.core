import logging

logger = logging.getLogger("Rapido")


def on_compilation_error(event):
    message = """%s
%s
%s""" % (
        event.message,
        event.error.text.replace('\n', ''),
        '-' * (event.error.offset - 1) + '^',
    )
    app = event.container.app
    event.container.app._messages.append(
        "Rapido compilation error - %s:\n%s" % (app.context.id, message)
    )
    logger.error(message)


def on_execution_error(event):
    app = event.container.app
    event.container.app._messages.append(
        "Rapido execution error - %s:\n   %s" % (
            app.context.id,
            event.message.replace(',   ','\n   ')
        )
    )
    logger.error(event.message)
