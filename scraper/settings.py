import logging
import os

MONGO_DSN = os.getenv("MONGO_DSN", "mongodb://admin:secret@mongo-poems-scraper:27017")

DEFAULT_HTTP_RETRIES = int(os.getenv("HTTP_RETRIES", 5))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(integration)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "filters": {"integration": {"()": "scraper.utils.logger.IntegrationFilter"},},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": os.getenv("LOGGING_LEVEL", default=logging.ERROR),
            "formatter": "default",
            "filters": ["integration"],
        },
    },
    "root": {"level": logging.WARNING, "handlers": ["console"],},
    "loggers": {
        "scraper": {
            "level": logging.DEBUG,
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

EXPORT_DATA_PATH = os.getenv("EXPORT_DATA_PATH", "/opt/data")
