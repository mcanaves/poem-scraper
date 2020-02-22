from collections import namedtuple
from typing import Dict, List

import click
import httpx
from parsel import Selector

from scraper.utils import coro

DATA_URL = "https://www.poetryfoundation.org/ajax/poems"


Category = namedtuple("Category", ("name", "slug"))


def parse_categories(raw_data: List[Dict]) -> List[Category]:
    return [Category(c["name"], c["slug"]) for c in raw_data]


async def get_poems_categories(ss: httpx.AsyncClient) -> List[Category]:
    response = await ss.get(DATA_URL)
    response_data = response.json()
    categories_data = next(
        f["categories"]
        for f in response_data["Filters"]
        if f["slug"] == "school-period"
    )
    return parse_categories(categories_data)


@click.command()
@coro
async def main():
    """
    Poetry Foundation Scraper.

    Simple web scraper that scrapes poems from the Poetry Foundation
    website into a single txt file.
    """
    async with httpx.AsyncClient(http2=True) as client:
        categories = await get_poems_categories(client)


if __name__ == "__main__":
    main()
