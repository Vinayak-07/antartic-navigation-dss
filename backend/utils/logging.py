"""Logging configuration helpers.

TODO: Define structured logging for service execution and monitoring.
"""

import logging


def get_logger(name: str):
    """Return a logger with a basic configuration.

    This is a simple placeholder for future instrumentation.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
