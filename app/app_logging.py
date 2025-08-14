import logging

from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("app")
logger.handlers = [RichHandler(rich_tracebacks=True)]
logger.level = logging.DEBUG
logger.propagate = False
