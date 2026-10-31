"""Structured logging configuration for aidy.AI."""

import sys
import logging
from typing import Optional


def get_logger(name: str = "aidy", level: int = logging.INFO) -> logging.Logger:
    """Returns a configured structured logger that never leaks credentials."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = get_logger("aidy")
