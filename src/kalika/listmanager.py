from pathlib import Path
from typing import Dict, List, Optional, Union, cast

import orjsonl


def find_missing_sites(list_path: Union[Path, str], directory_path: str):
    """Display missing sites by comparing list of URLs with WARC output directory."""
    list_path = Path(list_path)
    if list_path.suffix == ".txt":
        url_list = list_path.read_text().splitlines()
    elif list_path.suffix == ".jsonl":
        domain_list: List[Dict[str, str]] = cast("list", orjsonl.load(list_path))
        url_list = ["https://" + item["domain"] for item in domain_list]
    else:
        raise NotImplementedError(f"Unrecognized file type: {list_path.suffix}")
    directory_list = sites_from_warc_directory(directory_path)
    directory_list = [f"https://{item}" for item in directory_list]
    missing = sorted(set(url_list) - set(directory_list))
    return missing


def find_missing_sites_ordered(list_path: Union[Path, str], directory_path: str):
    """Display missing sites, ordered."""

    directory_list = sites_from_warc_directory(directory_path)
    directory_list = [f"https://{item}" for item in directory_list]

    domain_list: List[Dict[str, str]] = cast("list", orjsonl.load(list_path))
    missing = []
    for domain_item in domain_list:
        item = f"https://{domain_item['domain']}"
        if item not in directory_list:
            missing.append(item)
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


def chunk_listfile(list_path: Union[Path, str], chunk_size: Optional[int] = 500):
    """Chunk URL list file into equal chunks."""
    list_path = Path(list_path)
    items = Path(list_path).read_text().splitlines()
    chunks = chunk_list(items, chunk_size)
    for i, c in enumerate(chunks):
        chunkfile = list_path.parent / (
            Path(list_path).stem + f"-{i:02d}" + list_path.suffix
        )
        chunkfile.write_text("\n".join(c))


def chunk_list(items, n):
    """Chunk a list into equal chunks."""
    return [items[i : i + n] for i in range(0, len(items), n)]
