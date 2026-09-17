import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from tabulate import tabulate

from kalika.curation import ArchiveCuration
from kalika.heritrix import Crawler
from kalika.listmanager import (
    chunk_listfile,
    find_missing_sites,
    find_missing_sites_ordered,
)
from kalika.model import CrawlerInfo, CrawlerManager
from kalika.util import read_config, setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option("--config", type=str, envvar="KALIKA_CONFIG", help="Path to config file")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.version_option()
@click.pass_context
def main(ctx: click.Context, config: str, verbose: bool, debug: bool):
    setup_logging()
    logger.info("Welcome to Kalika")

    ctx.meta["config"] = {}
    if config:
        ctx.meta["config"] = read_config(config)


@main.group()
@click.option(
    "--heritrix-url", type=str, envvar="HERITRIX_URL", help="Heritrix server URL"
)
@click.pass_context
def heritrix(ctx: click.Context, heritrix_url: str):
    """Send commands to the Heritrix crawler."""
    if ctx.meta["config"]:
        pass
    elif heritrix_url:
        ctx.meta["config"] = {"heritrix": {"servers": [heritrix_url]}}
    else:
        raise ValueError("Environment variable KALIKA_CONFIG or HERITRIX_URL not set")

    crawlers: List[CrawlerInfo] = []
    for server in ctx.meta["config"]["heritrix"]["servers"]:
        crawler = Crawler(heritrix_url=server)
        cinfo = CrawlerInfo(name=server, instance=crawler)
        crawlers.append(cinfo)
    ctx.meta["mgr"] = CrawlerManager(crawlers=crawlers)


@heritrix.command()
@click.pass_context
@click.argument("item", help="Item to crawl: Single URL or file with multiple URLs")
@click.option(
    "--crawler", "crawler_index", type=int, help="Crawler number to dispatch to (0-x)"
)
def add(ctx: click.Context, item: str, crawler_index: Optional[int] = None):
    """Add one or multiple items to the crawler."""
    mgr: CrawlerManager = ctx.meta["mgr"]
    if crawler_index is not None:
        crawler_info = mgr.get_crawler_by_index(crawler_index)
    else:
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


@heritrix.command()
@click.argument("path", help="Path to output directory")
@click.option(
    "--crawler", "crawler_index", type=int, help="Crawler number to dispatch to (0-x)"
)
@click.pass_context
def drain(ctx: click.Context, path: str, crawler_index: Optional[int] = None):
    """Drain WARC files from the crawler."""
    if not Path(path).exists():
        logger.error("Path does not exist: %s", path)
        sys.exit(1)
    mgr: CrawlerManager = ctx.meta["mgr"]
    if crawler_index is not None:
        crawler_info = mgr.get_crawler_by_index(crawler_index)
    elif len(mgr.crawlers) == 1:
        crawler_info = mgr.get_crawler_by_index(0)
    else:
        raise ValueError("No or too many crawlers have been selected")
    logger.info(
        "Selected crawler: %s (%s jobs)", crawler_info.name, crawler_info.jobcount
    )
    crawler = crawler_info.instance
    crawler.finish_jobs(path)


@heritrix.command()
@click.pass_context
def list_jobs(ctx: click.Context):
    """Display list of crawler jobs."""
    mgr: CrawlerManager = ctx.meta["mgr"]
    for crawler_info in mgr.crawlers:
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


@main.group()
@click.pass_context
def urllist(ctx: click.Context):
    """Tools for working with URL lists."""
    pass


@urllist.command()
@click.option("--url-list", type=str, required=True, help="Path to URL list file")
@click.option(
    "--directory", type=str, required=True, help="Path to downloaded WARC files"
)
@click.option(
    "--ordered",
    is_flag=True,
    type=bool,
    required=False,
    default=False,
    help="Whether to process the input file in order",
)
@click.pass_context
def compare(
    ctx: click.Context, url_list: str, directory: str, ordered: Optional[bool] = False
):
    """Display list of missing sites."""
    if ordered:
        missing = find_missing_sites_ordered(url_list, directory)
    else:
        missing = find_missing_sites(url_list, directory)
    print("\n".join(missing))  # noqa: T201


@urllist.command()
@click.argument("url_list", help="Path to input list")
@click.option(
    "--chunk-size",
    type=int,
    default=500,
    required=False,
    help="Chunk size (default 500)",
)
@click.pass_context
def chunk(ctx: click.Context, url_list: str, chunk_size: Optional[int] = 500):
    """Partition list into equal sized chunks."""
    chunk_listfile(url_list, chunk_size)


@main.group()
@click.pass_context
def curate(ctx: click.Context):
    """Tools for curating web archives."""
    pass


@curate.command()
@click.argument("directory", help="Path to WARC files")
@click.pass_context
def to_wacz(ctx: click.Context, directory: str):
    """Convert all WARC files to WACZ files."""
    archive = ArchiveCuration(directory=directory)
    archive.to_wacz()
