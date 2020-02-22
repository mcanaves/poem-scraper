import asyncio
from functools import wraps


def coro(f):
    """
    Decorator to allow click work with asyncio.
    related: https://github.com/pallets/click/issues/85#issuecomment-43378930
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper
