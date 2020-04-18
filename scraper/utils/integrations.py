from contextvars import ContextVar
from functools import wraps
from typing import Type

import httpx

from scraper.integrations import registry
from scraper.integrations.base import Integration

_integration_ctx_var: ContextVar[str] = ContextVar("intengration_name", default="")


def _load_integration(source: str) -> Type[Integration]:
    scraper = registry.get(source)
    if not scraper:
        raise ValueError(
            f"No integration found for `{source}` source. Please, ensure it's in the source registry."
        )
    return scraper


def integration(fnx):
    @wraps(fnx)
    async def _wraps(source: str, *args):
        integration = _load_integration(source)
        _integration_ctx_var.set(source)
        async with httpx.AsyncClient(http2=True) as client:
            return await fnx(source, integration(ss=client), *args)

    return _wraps
