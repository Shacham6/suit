import logging

import rich.logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[rich.logging.RichHandler(
        markup=True,
        rich_tracebacks=True,
    )],
)

info = logging.info
debug = logging.debug
error = logging.error
warn = logging.warn
