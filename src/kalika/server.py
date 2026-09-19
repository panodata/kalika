import logging
import os
from typing import Optional

from wcmatch import glob

logger = logging.getLogger(__name__)


def run_wayback(
    spool_directory: str,
    archive_directory: Optional[str] = None,
    port: Optional[int] = None,
):
    """
    Run pywb's wayback server.
    https://pywb.readthedocs.io/

    :param spool_directory: Directory to run wayback on.
    :param archive_directory: Path to WARC or WACZ files.
    :param port: HTTP port to run wayback on. Default: 1142.
    """
    from pywb.apps.cli import wayback
    from pywb.manager.manager import CollectionsManager

    # Initialize collection directory.
    cwd = os.getcwd()
    os.chdir(spool_directory)
    m = CollectionsManager(coll_name="default", must_exist=False)
    try:
        m.add_collection()
    except FileExistsError:
        pass
    os.chdir(cwd)

    if archive_directory:
        archives = glob.glob(
            str(archive_directory) + "/*.{wacz,warc.gz}", flags=glob.BRACE
        )
        logger.info(f"Found {len(archives)} WARC/WACZ files")
        m.add_archives(archives, unpack_wacz=True)

    # Run wayback server.
    port = port or 1142
    wayback(
        [
            f"--directory={spool_directory}",
            f"--port={port}",
            "--all-coll=all",
            "--live",
            "--record",
            "--autoindex",
            # "--auto-interval=5",
            "--debug",
        ]
    )
