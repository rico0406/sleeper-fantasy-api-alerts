import logging
import os
from pathlib import Path
from typing import Dict

# Directory for all log files
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# Keep a registry of created loggers to avoid duplicates
_loggers: Dict[str, logging.Logger] = {}


def get_logger(alert_type: str) -> logging.Logger:
    """
    Return a logger configured for a specific alert type.
    Creates a new logger if it doesn't exist yet.

    Args:
        alert_type (str): Type of alert (e.g., 'weekly', 'daily', 'live').

    Returns:
        logging.Logger: Configured logger instance.
    """
    if alert_type in _loggers:
        return _loggers[alert_type]

    # Create logger
    logger = logging.getLogger(f"{alert_type}_logger")
    logger.setLevel(logging.INFO)

    # File handler
    log_file = LOG_DIR / f"{alert_type}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Stream handler (to also show in GitHub Actions logs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Attach handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Avoid duplicate messages if logger already exists
    logger.propagate = False

    # Register
    _loggers[alert_type] = logger

    return logger
