import logging.config

import click

from scraper import settings
from scraper.interactors import export_data as export_data_interactor
from scraper.interactors import list_sources as list_sources_interactor
from scraper.interactors import scrape_categories as scrape_categories_interactor
from scraper.interactors import scrape_index as scrape_index_interactor
from scraper.interactors import scrape_poems as scrape_poems_interactor
from scraper.repositories.mongo import MongoCategoryRepository, MongoPoemRepository
from scraper.utils.click import coro


@click.group()
def cli():
    """
    Poem Scrapers.

    Simple tool that scrapes poems from different sources.
    """


@click.command()
def list_sources():
    """
    Show all available scraping sources.
    """
    sources = list_sources_interactor()
    click.echo("\n".join(sources))


@click.command()
@click.argument("source")
@click.option(
    "--generate-index",
    is_flag=True,
    help="Generate poems index. If existing poems match with new index data the previous ones will be lost.",
)
@coro
async def scrape_source(source: str, generate_index: bool):
    """
    Start scraping a source.
    """
    if source not in list_sources_interactor():
        click.secho(
            "Invalid source. Please check `list_sources` command to see all available sources.",
            fg="red",
        )
        return

    category_respository = MongoCategoryRepository()
    poem_repository = MongoPoemRepository()
    if generate_index:
        await scrape_categories_interactor(source, category_respository)
        await scrape_index_interactor(source, category_respository, poem_repository)
    await scrape_poems_interactor(source, poem_repository)
    click.secho(f"Scraped {source}", fg="green")


@click.command()
@coro
async def export_data():
    """
    Export data by creating the categories as folders and the poems as text files.
    """
    category_respository = MongoCategoryRepository()
    poem_repository = MongoPoemRepository()
    if await export_data_interactor(category_respository, poem_repository):
        click.secho("Data successfully exported.", fg="green")
    else:
        click.secho(
            "An error occurred while exporting data. Please check the logs.", fg="red"
        )


cli.add_command(list_sources)
cli.add_command(scrape_source)
cli.add_command(export_data)


if __name__ == "__main__":
    logging.config.dictConfig(settings.LOGGING)
    cli()
