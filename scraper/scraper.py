import asyncio
import logging
from collections import namedtuple
from math import ceil
from typing import Dict, List, Optional

import click
import httpx
from parsel import Selector

from scraper.utils import coro

DATA_URL = "https://www.poetryfoundation.org/ajax/poems"
FILTER_QUERY = "?page={}&school-period={}"

logger = logging.getLogger(__name__)

Category = namedtuple("Category", ("name", "slug"))
Poem = namedtuple("Poem", ("title", "author", "link"))


def parse_poems(raw_data: List[Dict]) -> List[Poem]:
    return [Poem(p["title"], p["author"], p["link"]) for p in raw_data]


def parse_categories(raw_data: List[Dict]) -> List[Category]:
    return [Category(c["name"], c["slug"]) for c in raw_data]


async def get_poems_categories(ss: httpx.AsyncClient) -> List[Category]:
    logger.info("Getting poems periods.")
    response = await ss.get(DATA_URL)
    response_data = response.json()
    categories_data = next(
        f["categories"]
        for f in response_data["Filters"]
        if f["slug"] == "school-period"
    )
    categories = parse_categories(categories_data)
    logger.debug(f"Getted {len(categories)} periods.")
    return categories


async def get_poems_list(
    ss: httpx.AsyncClient, period: str, page: int = 1
) -> Optional[List[Dict]]:
    filter_query = FILTER_QUERY.format(page, period)
    response = await ss.get(DATA_URL + filter_query)
    return response.json()


async def get_poems(ss: httpx.AsyncClient, period: str) -> List[Poem]:
    logger.info(f"Getting {period} period poems.")
    response = await get_poems_list(ss, period)
    poems = response.get("Entries", [])
    pages = ceil(response.get("TotalResults", 0) / 20)
    for page in range(2, pages + 1):
        response = await get_poems_list(ss, period)
        poems.extend(response["Entries"])
    poems = parse_poems(poems)
    logger.debug(f"Getted {len(poems)} poems of the period {period}.")
    return poems


@click.command()
@coro
async def main():
    """
    Poetry Foundation Scraper.

    Simple web scraper that scrapes poems from the Poetry Foundation
    website into a single txt file.
    """
    logger.info(f"Start scraping Poetry Fundation.")
    async with httpx.AsyncClient(http2=True) as client:
        categories = await get_poems_categories(client)
        poems_requests = [get_poems(client, c.slug) for c in categories]
        await asyncio.gather(*poems_requests)


if __name__ == "__main__":
    formatter = logging.Formatter("[%(levelname)s %(asctime)8s] %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    main()
