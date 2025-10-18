import logging
import os
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import Dict

# Directory for all log files
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Registry to avoid duplicated loggers
_loggers: Dict[str, logging.Logger] = {}

# Keep 3 weekly backups
LOG_BACKUP_COUNT = 3

# Rotate logs weekly at Wednesday (W2)
LOG_ROTATION_TIME = "W2"


def get_logger(alert_type: str) -> logging.Logger:
    """
    Return a logger configured for a specific alert type with weekly rotation.
    Logs are rotated once per week and old files are automatically cleaned.

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

    # --- File handler with weekly rotation ---
    log_dir = os.path.join(LOG_DIR, alert_type)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{alert_type}.log")
    rotating_handler = TimedRotatingFileHandler(
        filename=log_file,
        when=LOG_ROTATION_TIME,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
        utc=True
    )

    # --- Console handler (for GitHub Actions output) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # --- Formatter ---
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    rotating_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # --- Attach handlers ---
    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)

    # Avoid duplicate messages if logger already exists
    logger.propagate = False

    # Store reference to avoid duplicates
    _loggers[alert_type] = logger

    return logger
