"""
Day 6 - Structured application logging.
"""

import logging
import sys


def configure_logging() -> None:
    """Configure application-wide logging."""

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
    )


def get_logger(
    name: str,
) -> logging.Logger:

    return logging.getLogger(name)

