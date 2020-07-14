from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, Optional


class BaseEntity:
    @classmethod
    def from_dict(cls, adict: Dict) -> BaseEntity:
        raise NotImplementedError

    def to_dict(self) -> Dict:
        """Return class attributes in a dictionary."""
        return asdict(self)


@dataclass
class Category(BaseEntity):
    name: str
    source: str
    internal_id: str = field(repr=False)

    @classmethod
    def from_dict(cls, adict: Dict) -> Category:
        return cls(
            name=adict["name"],
            source=adict["source"],
            internal_id=adict["internal_id"],
        )


@dataclass
class Poem(BaseEntity):
    title: str
    author: str
    category: str = field(repr=False)
    link: str = field(repr=False)
    text: Optional[str] = field(repr=False, default=None)
    scraped: Optional[bool] = False

    @classmethod
    def from_dict(cls, adict: Dict) -> Poem:
        return cls(
            title=adict["title"],
            author=adict["author"],
            category=adict["category"],
            link=adict["link"],
            text=adict.get("text"),
            scraped=adict.get("scraped"),
        )
