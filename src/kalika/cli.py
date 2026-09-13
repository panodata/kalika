import logging
import sys
from pathlib import Path
from typing import List

import click
from tabulate import tabulate

from kalika.heritrix import Crawler
from kalika.model import CrawlerInfo, CrawlerManager
from kalika.util import read_config, setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
@click.option(
    "--config", type=str, envvar="HERITRIX_CONFIG", help="Path to config file"
)
@click.option(
    "--heritrix-url", type=str, envvar="HERITRIX_URL", help="Heritrix server URL"
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(
    ctx: click.Context, config: str, heritrix_url: str, verbose: bool, debug: bool
):
    setup_logging()
    logger.info("Welcome to Kalika")

    if config:
        ctx.meta["config"] = read_config(config)
    elif heritrix_url:
        ctx.meta["config"] = {"heritrix": {"servers": [heritrix_url]}}
    else:
        raise ValueError("Environment variable HERITRIX_CONFIG or HERITRIX_URL not set")

    crawlers: List[CrawlerInfo] = []
    for server in ctx.meta["config"]["heritrix"]["servers"]:
        crawler = Crawler(heritrix_url=server)
        cinfo = CrawlerInfo(name=server, instance=crawler)
        crawlers.append(cinfo)
    ctx.meta["mgr"] = CrawlerManager(crawlers=crawlers)


@main.command()
@click.pass_context
@click.argument("item", help="Item to crawl: URL or file with URLs")
def add(ctx: click.Context, item: str):
    """Add one or multiple items to the crawler."""
    mgr: CrawlerManager = ctx.meta["mgr"]
    crawler_info = mgr.get_preferred_crawler()
    logger.info(
        "Selected crawler: %s (%s jobs)", crawler_info.name, crawler_info.jobcount
    )
    crawler = crawler_info.instance
    if Path(item).is_file():
        crawler.add_file(item)
    elif item.startswith("http://") or item.startswith("https://"):
        crawler.add_url(item)
    else:
        logger.error("Item is not a file or url: %s", item)
        sys.exit(1)


@main.command()
@click.pass_context
@click.argument("path", help="Path to output directory")
@click.argument("crawler_index", help="Crawler index")
def drain(ctx: click.Context, path: str, crawler_index: int):
    """Drain WARC file from the crawler."""
    if not Path(path).exists():
        logger.error("Path does not exist: %s", path)
        sys.exit(1)
    mgr: CrawlerManager = ctx.meta["mgr"]
    crawler = mgr.crawlers[crawler_index].instance
    crawler.finish_jobs(path)


@main.command()
@click.pass_context
def list_jobs(ctx: click.Context):
    """Display list of crawler jobs."""
    for crawler_info in ctx.meta["crawler"]:
        print(f"Running jobs for crawler: {crawler_info.name}")  # noqa: T201
        crawler = crawler_info.instance
        try:
            jobs = crawler.get_jobs()
        except Exception as e:
            logger.warning(
                "Failed to get jobs for crawler: %s. Error: %s", crawler_info.name, e
            )
            continue
        print(tabulate(jobs, headers="keys"))  # noqa: T201
        print()  # noqa: T201
