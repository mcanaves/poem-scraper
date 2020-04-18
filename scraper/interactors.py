import asyncio
import logging
from itertools import chain, islice
from typing import List

from scraper.integrations import registry
from scraper.integrations.base import Integration
from scraper.repositories.base import CategoryRepository, PoemRepository
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
    logger.info(f"Scraping poems categories")
    categories = await integration.scrape_categories()
    await repository.bulk_create(categories)
    logger.info(f"Scraped {len(categories)} poems categories")


@integration
async def scrape_index(
    source: str,
    integration: Integration,
    category_repository: CategoryRepository,
    poem_repository: PoemRepository,
):
    async def operation(category):
        logger.info(f"Scraping {category.name} poems index")
        poems = await integration.scrape_poems_index(category)
        await poem_repository.bulk_create(poems)
        logger.info(f"Scraped {category.name} poems index with {len(poems)} poems")

    categories = await category_repository.list(source)
    await asyncio.gather(*(operation(c) for c in categories))


@integration
async def scrape_poems(
    source: str, integration: Integration, repository: PoemRepository,
):
    async def operation(poem):
        logger.debug(f"Scraping {poem.title} poem")
        if (updated_poem := await integration.scrape_poem(poem)) :
            await repository.create(updated_poem)

    logger.info("Scraping poems")
    poems = await repository.list(source=source, only_not_scraped=True)
    poems_chunks = (chain([p], islice(poems, 20 - 1)) for p in poems)
    for chunk in poems_chunks:
        await asyncio.gather(*(operation(p) for p in chunk))
    logger.info("Scraped poems")
