from difflib import unified_diff
from pathlib import Path


def find_missing_sites(list_path: str, directory_path: str):
    """Display missing sites by comparing list of URLs with WARC output directory."""
    url_list = Path(list_path).read_text().splitlines()
    directory_list = sites_from_warc_directory(directory_path)
    directory_list = [f"https://{item}" for item in directory_list]
    diff = unified_diff(url_list, directory_list)
    missing = [item.lstrip("-") for item in diff if item.startswith("-")]
    return missing


def sites_from_warc_directory(warc_directory: str):
    """
    Derive sites from WARC directory.

    A typical layout of a list of per-site WARC files can look like this:

    zagueros.noblogs.org-00000.warc.gz
    zagueros.noblogs.org-00001.warc.gz
    zagueros.noblogs.org-00002.warc.gz

    Derive it into a single item `zagueros.noblogs.org`.
    """
    items = []
    for candidate in sorted(Path(warc_directory).glob("*.warc.gz")):
        name = candidate.with_suffix("").with_suffix("").name.rstrip("-0123456789")
        items.append(name)
    items = sorted(set(items))
    return items
