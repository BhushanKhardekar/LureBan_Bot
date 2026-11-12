import logging
import sys
from typing import TextIO

import colorlog


def _create_console_handler() -> logging.StreamHandler[TextIO]:
    """Return a coloured StreamHandler for console output."""
    handler: logging.StreamHandler[TextIO] = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        colorlog.ColoredFormatter(  # type: ignore[misc]
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    return handler


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, creating and configuring it on first call."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.addHandler(_create_console_handler())
    return logger
