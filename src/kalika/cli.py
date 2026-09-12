import logging
import sys
from pathlib import Path

import click

from kalika.heritrix import Crawler
from kalika.util import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option("--heritrix-url", type=str, envvar="HERITRIX_URL")
@click.option("-v", "--verbose", is_flag=True)
@click.option("--debug", is_flag=True)
def main(ctx: click.Context, heritrix_url: str, verbose: bool, debug: bool):
    ctx.params["heritrix_url"] = heritrix_url
    setup_logging()
    logger.info("Welcome to Kalika")


@main.command()
@click.pass_context
@click.argument("item")
def add(ctx: click.Context, item: str):
    """Add one or multiple items to the crawler."""
    if ctx.parent is None:
        raise ValueError("Needs a parent context")
    heritrix_url = ctx.parent.params["heritrix_url"]
    crawler = Crawler(heritrix_url=heritrix_url)
    if Path(item).is_file():
        crawler.add_file(item)
    elif item.startswith("http://") or item.startswith("https://"):
        crawler.add_url(item)
    else:
        logger.error("Item is not a file or url: %s", item)
        sys.exit(1)
