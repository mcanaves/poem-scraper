from typing import List, Optional

import motor.motor_asyncio
from pymongo import ReplaceOne

from scraper import settings
from scraper.entities import Category, Poem


class CategoryRepository:
    async def list(self, source: Optional[str] = None) -> List[Category]:
        raise NotImplementedError

    # TODO: only create if exist nothing
    async def bulk_create(self, categories: List[Category], upsert: bool = True):
        raise NotImplementedError


class PoemRepository:
    # TODO: batch
    async def list(
        self, source: Optional[str] = None, only_indexed: bool = False
    ) -> List[Poem]:
        raise NotImplementedError

    # TODO: only create if exist nothing
    async def create(self, poem: Poem, upsert: bool = True):
        raise NotImplementedError

    async def bulk_create(self, poems: List[Poem], upsert: bool = True):
        raise NotImplementedError


class MongoBaseRepository:
    def __init__(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DSN)
        self.db = client.poetry


# TODO: refactor repo to same and load onyl change collections
class MongoCategoryRepository(MongoBaseRepository, CategoryRepository):
    def __init__(self):
        super().__init__()
        self.colletion = self.db.categories

    async def list(self, source: Optional[str] = None) -> List[Category]:
        query = {"source": {"$eq": source}} if source else {}
        result = await self.colletion.find(query).to_list(None)
        return [Category.from_dict(r) for r in result]

    async def bulk_create(self, categories: List[Category], upsert: bool = True):
        await self.colletion.bulk_write(
            [
                ReplaceOne(
                    {"source": c.source, "internal_id": c.internal_id},
                    c.to_dict(),
                    upsert=upsert,
                )
                for c in categories
            ]
        )


class MongoPoemRepository(MongoBaseRepository, PoemRepository):
    def __init__(self):
        super().__init__()
        self.colletion = self.db.poems

    async def list(
        self, source: Optional[str] = None, only_indexed: bool = False
    ) -> List[Poem]:
        query = {"category.source": {"$eq": source}} if source else {}
        if only_indexed:
            query = {"$and": [query, {"text": {"$eq": None}}]}
        result = await self.colletion.find(query).to_list(None)
        return [
            Poem.from_dict({**r, "category": Category.from_dict(r["category"])})
            for r in result
        ]

    async def create(self, poem: Poem, upsert: bool = True):
        await self.colletion.replace_one(
            {"category.source": poem.category.source, "link": poem.link},
            poem.to_dict(),
            upsert=upsert,
        )

    async def bulk_create(self, poems: List[Poem], upsert: bool = True):
        await self.colletion.bulk_write(
            [
                ReplaceOne(
                    {"category.source": p.category.source, "link": p.link},
                    p.to_dict(),
                    upsert=upsert,
                )
                for p in poems
            ]
        )
