from typing import Optional


def run_wayback(directory: str, port: Optional[int] = None):
    """
    Run pywb's wayback server.
    https://pywb.readthedocs.io/

    :param directory: Directory to run wayback on.
    :param port: HTTP port to run wayback on. Default: 1142.
    """
    from pywb.apps.cli import wayback

    port = port or 1142
    wayback(
        [
            f"--directory={directory}",
            f"--port={port}",
            "--live",
            "--record",
            "--autoindex",
            # "--auto-interval=5",
            "--debug",
        ]
    )
