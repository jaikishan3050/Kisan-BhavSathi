"""Basic application logging configuration.

Sets up standard Python logging with consistent timestamps and formatting.
"""

import logging
import sys
from app.core.config import get_settings


def setup_logging() -> None:
    """Configure the root application logger according to active settings."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Ensure uvicorn access logs propagate cleanly
    logging.getLogger("uvicorn.access").setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance for a given module."""
    return logging.getLogger(name)
