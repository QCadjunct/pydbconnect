"""Simple logging setup."""

import logging
from typing import Optional


def setup_logging(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Setup basic logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if log_file:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        logger.addHandler(handler)

    return logger
