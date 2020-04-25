import logging

from scraper.utils.integrations import _integration_ctx_var


class IntegrationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.__dict__.update({"integration": _integration_ctx_var.get()})
        return True
