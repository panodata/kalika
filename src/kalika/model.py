from dataclasses import dataclass, field
from operator import attrgetter
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from heritrix import Crawler


@dataclass
class CrawlerInfo:
    """Manage a crawler and its name."""

    name: str
    instance: "Crawler"
    jobcount: Optional[int] = 0


@dataclass
class CrawlerManager:
    """Manage multiple crawlers."""

    crawlers: List[CrawlerInfo] = field(default_factory=list)

    def get_crawler_by_index(self, index: int) -> CrawlerInfo:
        """Get crawler by index."""
        return self.crawlers[index]

    def get_preferred_crawler(self) -> CrawlerInfo:
        """Get crawler with the lowest job count."""
        for crawler_info in self.crawlers:
            info = crawler_info.instance.info()
            if info["engine"]["jobs"]:
                jobcount = len(info["engine"]["jobs"]["value"])
            else:
                jobcount = -1
            crawler_info.jobcount = jobcount

        reverse_sorted_by_job_count = sorted(self.crawlers, key=attrgetter("jobcount"))
        return reverse_sorted_by_job_count[0]
