"""Logging helpers for the warehouse onboarding assistant."""

from __future__ import annotations

import logging

from .config import LOG_LEVEL


def configure_logging(level: str | int = LOG_LEVEL) -> None:
    """Configure application logging once for production or local runs.

    Args:
        level: Logging level to apply to the root logger.
    """

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger.

    Args:
        name: Logger name, usually ``__name__``.

    Returns:
        A configured logger instance.
    """

    return logging.getLogger(name)

