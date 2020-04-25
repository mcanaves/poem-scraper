import logging
from functools import update_wrapper
from typing import Optional

from scraper import settings

logger = logging.getLogger(__name__)


class Retry:
    def __init__(
        self,
        excepts: Optional[tuple] = None,
        max_retries: int = settings.DEFAULT_HTTP_RETRIES,
    ):
        self._excepts = excepts or Exception
        self._max_retries = max_retries

    def __call__(self, fnx):
        async def decorated(*args: list, **kwargs: dict):
            last_exception = Exception(
                f"Something weird happend retrying  {fnx.__name__}"
            )

            for retry in range(self._max_retries):
                try:
                    return await fnx(*args, **kwargs)
                except self._excepts as ex:
                    last_exception = ex
                    logger.warning(
                        f"Retrying {fnx.__name__} execution. Retry {retry+1}"
                    )
            raise last_exception

        update_wrapper(self, fnx, updated=[])
        return decorated
