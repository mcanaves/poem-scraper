from typing import List

import httpx

from scraper.entities import Category, Poem


class Integration:

    INTEGRATION_NAME = "base"

    def __init__(self, ss: httpx.AsyncClient):
        self.ss = ss

    async def scrape_categories(self) -> List[Category]:
        raise NotImplementedError

    async def scrape_poems_index(self, category: Category) -> List[Poem]:
        raise NotImplementedError

    async def scrape_poem(self, Poem) -> Poem:
        raise NotImplementedError
