from typing import List, Optional

from scraper.entities import Category, Poem


class CategoryRepository:
    async def list(self, source: Optional[str] = None) -> List[Category]:
        raise NotImplementedError

    async def bulk_create(self, categories: List[Category], upsert: bool = True):
        raise NotImplementedError


class PoemRepository:
    async def list(
        self, source: Optional[str] = None, only_not_scraped: bool = False
    ) -> List[Poem]:
        raise NotImplementedError

    async def create(self, poem: Poem, upsert: bool = True):
        raise NotImplementedError

    async def bulk_create(self, poems: List[Poem], upsert: bool = True):
        raise NotImplementedError
