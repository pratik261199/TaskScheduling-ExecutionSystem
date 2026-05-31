import logging
import logging.config
from pathlib import Path

def setup_logging():
    """Set up logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "executor.log"

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file,
                "maxBytes": 1024 * 1024 * 5,
                "backupCount": 5,
                "formatter": "default",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["file", "console"],
            "level": "INFO",
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
