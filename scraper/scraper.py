import click

from scraper.utils import coro


@click.command()
@coro
async def main():
    """
    Poetry Foundation Scraper.

    Simple web scraper that scrapes poems from the Poetry Foundation
    website into a single txt file.
    """
    pass


if __name__ == "__main__":
    main()
