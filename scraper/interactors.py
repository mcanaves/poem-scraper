import asyncio
import logging
from itertools import chain
from typing import List

from scraper.integrations import registry
from scraper.integrations.base import Integration
from scraper.repositories import CategoryRepository, PoemRepository
from scraper.utils.integrations import integration

logger = logging.getLogger(__name__)


def list_sources() -> List[str]:
    return list(registry.keys())


async def get_categories(source: str, repository: CategoryRepository):
    return [c.to_dict() for c in await repository.list(source)]


@integration
async def scrape_categories(
    source: str, integration: Integration, repository: CategoryRepository
):
    logger.info(f"Scraping `{source}` poems categories")
    categories = await integration.scrape_categories()
    await repository.bulk_create(categories)
    logger.debug(f"Scraped {len(categories)} `{source}` poems categories")


@integration
async def scrape_index(
    source: str,
    integration: Integration,
    category_repository: CategoryRepository,
    poem_repository: PoemRepository,
):
    async def operation(category):
        poems = await integration.scrape_poems_index(category)
        await poem_repository.bulk_create(poems)

    logger.info(f"Generating `{source}` poems index")
    categories = await category_repository.list(source)
    await asyncio.gather(*[operation(c) for c in categories])


@integration
async def scrape_poems(
    source: str, integration: Integration, repository: PoemRepository,
):
    # TODO: batch of 10 parallelas
    logger.info(f"Scraping `{source}` poems")
    poems = await repository.list(source=source, only_indexed=True)
    logger.debug(f"Scraping {len(poems)} {source} poems")
    for poem in poems:
        if (updated_poem := await integration.scrape_poem(poem)) :
            await repository.create(updated_poem)
    logger.debug(f"Scraped {source} poems")
