import json
import logging
from math import ceil
from typing import Dict, List, Optional

import httpx
from parsel import Selector

from scraper.entities import Category, Poem
from scraper.integrations.base import Integration
from scraper.utils.http import Retry

logger = logging.getLogger(__name__)


DATA_URL = "https://www.poetryfoundation.org/ajax/poems"
FILTER_QUERY = "?page={}&school-period={}"


@Retry(excepts=(httpx.TimeoutException,))
async def get_poems_index(
    ss: httpx.AsyncClient, period_slug: str, page: int = 1
) -> Optional[List[Dict]]:
    filter_query = FILTER_QUERY.format(page, period_slug)
    response = await ss.get(DATA_URL + filter_query, timeout=10.0)
    return response.json()


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
    poem.author = poem_data["author"]["name"]
    poem.title = poem_data["name"]
    poem.text = poem_data["text"]
    return poem


class PoetryFoundation(Integration):

    INTEGRATION_NAME = "poetry_foundation"

    async def scrape_categories(self) -> List[Category]:
        response = await self.ss.get(DATA_URL)
        data = response.json()
        return _parse_categories(data)

    async def scrape_poems_index(self, category: Category) -> List[Poem]:
        logger.debug(f"Scraping `{category.source}` {category.name} poems index")
        response = await get_poems_index(self.ss, category.internal_id)
        poems = response.get("Entries", [])
        pages = ceil(response.get("TotalResults", 0) / 20)
        for page in range(2, pages + 1):
            response = await get_poems_index(self.ss, category.internal_id, page)
            poems.extend(response.get("Entries", []))
        logger.debug(
            f"Generated `{category.source}` {category.name} poems index with {len(poems)} poems"
        )
        return _parse_poems_list(poems, category)

    @Retry(excepts=(httpx.TimeoutException,))
    async def scrape_poem(self, poem: Poem) -> Optional[Poem]:
        logger.debug(f"Scraping `{poem.category.source}` {poem.title} poem")
        response = await self.ss.get(poem.link, timeout=10.0)
        selector = Selector(response.text)
        json_ld_data = json.loads(
            selector.xpath('//script[@type="application/ld+json"]/text()').get()
        )
        try:
            return _update_poem(json_ld_data, poem)
        except Exception:
            logger.exception(
                f"Error parsing scrapeds poem {poem.title}. JSON_LD_DATA: {json_ld_data}"
            )

        return None
