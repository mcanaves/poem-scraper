import json
import logging
from math import ceil
from typing import Dict, List, Optional, Tuple

import httpx
from parsel import Selector

from scraper.entities import Category, Poem
from scraper.integrations.base import Integration
from scraper.utils.http import Retry

logger = logging.getLogger(__name__)


DATA_URL = "https://www.poetryfoundation.org/ajax/poems"
FILTER_QUERY = "?page={}&school-period={}"
PAGE_SIZE = 20
RETRY_EXCEPTS = (
    httpx.TimeoutException,
    httpx.NetworkError,
    httpx.ProtocolError,
)


@Retry(excepts=RETRY_EXCEPTS)
async def get_poems_index(
    ss: httpx.AsyncClient, period_slug: str, page: int = 1
) -> Tuple[List, int]:
    filter_query = FILTER_QUERY.format(page, period_slug)
    response = await ss.get(DATA_URL + filter_query, timeout=10.0)
    data = response.json()
    if not isinstance(data, dict):
        logger.error("Invalid index response. Period {period_slug}, page {page}.")
        return [], 0
    return data.get("Entries", []), ceil(data.get("TotalResults", 0) / PAGE_SIZE)


def _parse_categories(raw_data: List[Dict]) -> List[Category]:
    data = next(
        f["categories"] for f in raw_data["Filters"] if f["slug"] == "school-period"
    )

    return [
        Category.from_dict(
            {
                "name": d["name"],
                "source": PoetryFoundation.INTEGRATION_NAME,
                "internal_id": d["slug"],
            }
        )
        for d in data
    ]


def _parse_poems_list(raw_data: List[Dict], category: Category) -> List[Poem]:
    return [
        Poem.from_dict(
            {
                "title": p["title"],
                "author": p["author"],
                "link": p["link"],
                "category": category,
            }
        )
        for p in raw_data
    ]


def _update_poem(raw_data: Dict, poem: Poem) -> Poem:
    poem_data = next(
        (d for d in raw_data["@graph"] if d["@type"] == "CreativeWork"), None
    )
    poem.scraped = True
    if poem_data:
        poem.author = poem_data.get("author", {}).get("name")
        poem.title = poem_data.get("name")
        poem.text = poem_data.get("text")
    return poem


class PoetryFoundation(Integration):

    INTEGRATION_NAME = "poetry_foundation"

    async def scrape_categories(self) -> List[Category]:
        response = await self.ss.get(DATA_URL)
        data = response.json()
        return _parse_categories(data)

    async def scrape_poems_index(self, category: Category) -> List[Poem]:
        poems, pages = await get_poems_index(self.ss, category.internal_id)
        for page in range(2, pages + 1):
            new_poems, _ = await get_poems_index(self.ss, category.internal_id, page)
            poems.extend(new_poems)
        return _parse_poems_list(poems, category)

    @Retry(excepts=RETRY_EXCEPTS)
    async def scrape_poem(self, poem: Poem) -> Optional[Poem]:
        response = await self.ss.get(poem.link, timeout=10.0)
        selector = Selector(response.text)
        json_ld_data = json.loads(
            selector.xpath('//script[@type="application/ld+json"]/text()').get()
        )
        return _update_poem(json_ld_data, poem)
