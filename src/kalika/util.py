from __future__ import absolute_import

import logging
import os

import colorlog
import tomli
from colorlog.escape_codes import escape_codes


def setup_logging(
    level=logging.INFO, verbose: bool = False, debug: bool = False, width: int = 20
):
    if os.environ.get("DEBUG"):
        level = logging.DEBUG

    reset = escape_codes["reset"]
    log_format = (
        f"%(asctime)-15s [%(name)-{width}s] "
        f"%(log_color)s%(levelname)-8s:{reset} %(message)s"
    )

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(log_format))

    logging.basicConfig(format=log_format, level=level, handlers=[handler])

    logging.getLogger("urllib3.connectionpool").setLevel(level)

    if verbose:
        logging.getLogger("kalika").setLevel(logging.DEBUG)


def read_config(path: str):
    with open(path, "rb") as f:
        return tomli.load(f)
