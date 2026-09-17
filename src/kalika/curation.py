import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ArchiveCuration:
    """A few tools to curate the archive."""

    def __init__(self, directory: str):
        self.directory = directory

    def to_wacz(self):
        """Convert all WARC files to WACZ format."""
        # wacz create -o www.example.wacz www.example.org.warc.gz
        from wacz.main import main as run_wacz

        for warc_file in Path(self.directory).rglob("*.warc.gz"):
            wacz_file = warc_file.with_suffix("").with_suffix(".wacz")
            logger.info(f"Converting {warc_file} to WACZ format")
            logger.info(f"WACZ file: {wacz_file}")
            args = [
                "create",
                f"--output={wacz_file}",
                str(warc_file),
            ]
            run_wacz(args)
            warc_file.unlink()
