import re

from slugify import slugify


def strip_html(text: str) -> str:
    """Remove html tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def slugify_title(title: str) -> str:
    title = strip_html(title)
    return slugify(title)
