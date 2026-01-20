import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("app")
logger.level = logging.DEBUG
logger.propagate = False

# Optional nice formatting if `rich` is installed (not required for core runtime)
try:
    from rich.logging import RichHandler  # type: ignore

    logger.handlers = [RichHandler(rich_tracebacks=True)]
except Exception:
    # Fall back to standard logging handler.
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
