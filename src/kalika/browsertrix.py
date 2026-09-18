import logging
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from docker import DockerClient
from docker.errors import ContainerError

from kalika.model import CrawlerBase

logger = logging.getLogger(__name__)


class BrowsertrixCrawler(CrawlerBase):
    def __init__(self, directory: str):
        self.directory = Path(directory)
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.directory}")

    def add_url(self, url: str):
        """Add single URL or multiple URLs per textfile."""
        parsed_url = urlparse(url)
        job_name = parsed_url.hostname
        if job_name is None:
            logger.warning("Job name cannot be None")
            return

        collection_name = job_name.replace(".", "_")
        report_filename = f"{job_name}-report.json"
        wacz_directory = self.directory / "warc"
        report_file = self.directory / "report" / report_filename

        with tempfile.TemporaryDirectory() as tmpdir:
            crawls_path = Path(tmpdir)
            logger.info(
                "Processing '%s' in temporary directory '%s'", job_name, crawls_path
            )

            # Run crawler job.
            # --screenshot=fullPage
            d = DockerClient.from_env()
            try:
                d.containers.run(
                    image="docker.io/webrecorder/browsertrix-crawler",
                    command=f"""
                    crawl --url={url} --title='Archive of {job_name}' \
                        --collection={collection_name} \
                        --generateWACZ --statsFilename={report_filename} \
                        --sizeLimit=5000000000 --rolloverSize=1000000000 \
                        --timeLimit=3600""",
                    volumes={str(crawls_path): {"bind": "/crawls", "mode": "rw"}},
                    remove=True,
                    detach=False,
                )
            except ContainerError as e:
                logger.error("Crawling '%s' possibly failed: %s", job_name, e)

            # Collect outcome.
            try:
                shutil.copy(crawls_path / report_filename, report_file)
                for wacz in crawls_path.rglob("*.wacz"):
                    target_filename = wacz.name.replace("_", ".")
                    shutil.copy(wacz, wacz_directory / target_filename)
            except Exception as e:
                logger.error(
                    "Unable to extract files from temporary directory '%s': %s",
                    crawls_path,
                    e,
                )
