import logging
import os

MONGO_DSN = os.getenv("MONGO_DSN", "mongodb://admin:secret@mongo:27017")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": os.getenv("LOGGING_LEVEL", default=logging.ERROR),
            "formatter": "default",
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
