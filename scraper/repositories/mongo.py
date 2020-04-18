from typing import List, Optional

import motor.motor_asyncio
from pymongo import ReplaceOne

from scraper import settings
from scraper.entities import Category, Poem
from scraper.repositories.base import CategoryRepository, PoemRepository


class MongoBaseRepository:
    def __init__(self, collection: str):
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_DSN)
        self.colletion = client.poetry[collection]


class MongoCategoryRepository(MongoBaseRepository, CategoryRepository):
    def __init__(self):
        super().__init__("categories")

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
        super().__init__("poems")

    async def list(
        self, source: Optional[str] = None, only_not_scraped: bool = False
    ) -> List[Poem]:
        query = {"category.source": {"$eq": source}} if source else {}
        if only_not_scraped:
            query = {"$and": [query, {"scraped": {"$eq": False}}]}
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
