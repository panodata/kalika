import json
import logging
import re
import shutil
import tempfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import cast
from urllib.parse import urlparse

import pandas as pd
from heritrix3 import HeritrixAPI, disable_ssl_warnings

logger = logging.getLogger(__name__)


class Crawler:
    def __init__(self, heritrix_url: str):
        self.heritrix_url = heritrix_url
        disable_ssl_warnings()
        self.api = HeritrixAPI(
            host=heritrix_url,
            user="admin",
            passwd="admin",  # noqa: S106
            verbose=True,
        )

    def add_url(self, url: str):

        parsed_url = urlparse(url)
        job_name = parsed_url.hostname
        if job_name is None:
            raise ValueError("Job name cannot be None")
        logger.info("Adding job: %s", job_name)

        # dump info
        # pprint(self.api.info(raw=False))

        # FIXME: Use correct path to the package, not to the repository root.
        job_xml_path = Path("src/kalika/crawler-beans.cxml")
        job_xml = job_xml_path.read_text()
        job_xml = job_xml.replace("# Add seed URL here.", url)
        job_xml = job_xml.replace(
            "metadata.jobName=www.example.org", f"metadata.jobName={job_name}"
        )
        job_xml = job_xml.replace(
            "metadata.description=Conserving https://www.example.org",
            f"metadata.description=Conserving {url}",
        )

        tmpfile = NamedTemporaryFile()  # noqa: SIM115
        tmpfile.write(job_xml.encode("utf-8"))
        tmpfile.flush()

        self.api.create(job_name=job_name)
        # TODO: Only with `--force-recreate`
        # self.api.teardown(job_name=job_name)
        self.api.send_config(job_name=job_name, cxml_filepath=Path(tmpfile.name))

        logger.info("Building: %s", job_name)
        self.api.build(job_name=job_name)
        self.api.wait_for_action(job_name=job_name, action="build", poll_delay=0.25)

        logger.info("Launching: %s", job_name)
        self.api.launch(job_name=job_name)
        self.api.wait_for_action(job_name=job_name, action="launch", poll_delay=0.25)

    def add_file(self, path: str):
        urls = Path(path).read_text().splitlines()
        for url in urls:
            self.add_url(url)

    def get_jobs(self):
        # RUNNING, FINISHED
        jobs = self.api.list_jobs(status="RUNNING")
        data = []
        for job_name in sorted(jobs):
            job_info = cast(dict, cast(object, self.api.info(job_name=job_name)))
            # elapsedMilliseconds
            metadata = {
                "name": job_name,
                "time_elapsed": job_info["job"]["elapsedReport"]["elapsedPretty"],
                "rate_document": float(
                    job_info["job"]["rateReport"]["currentDocsPerSecond"]
                ),
                "rate_kilobyte": int(job_info["job"]["rateReport"]["currentKiBPerSec"]),
                "uri_queue": int(job_info["job"]["uriTotalsReport"]["queuedUriCount"]),
                "uri_total": int(job_info["job"]["uriTotalsReport"]["totalUriCount"]),
            }
            data.append(metadata)
        df = pd.DataFrame(data)
        if data:
            total = {
                "name": "total",
                "rate_document": df["rate_document"].sum(),
                "rate_kilobyte": df["rate_kilobyte"].sum(),
                "uri_queue": df["uri_queue"].sum(),
                "uri_total": df["uri_total"].sum(),
            }
            data.append(total)
        return data

    def finish_jobs(self, path: str):
        target_path = Path(path)
        # RUNNING, FINISHED
        jobs = self.api.list_jobs(status="FINISHED")
        for job_name in sorted(jobs):
            # if job_name != "foo.example.org":
            #    continue
            self.finish_job(job_name=job_name, target_path=target_path)

    def finish_job(self, job_name: str, target_path: str | Path):
        logger.info("Finishing job: %s", job_name)
        target_path = Path(target_path)
        # Save job metadata to JSON file.
        job_info = cast(dict, cast(object, self.api.info(job_name=job_name)))
        delete_keys = [
            "primaryConfigUrl",
            "url",
            "configFiles",
            "crawlLogTail",
            "reports",
            "alertLogFilePath",
            "alertLogFileUrl",
            "crawlLogFilePath",
            "crawlLogFileUrl",
        ]
        for delete_key in delete_keys:
            job_info["job"].pop(delete_key, None)
        job_info_path = Path(target_path / f"{job_name}-report.json")
        job_info_path.write_text(json.dumps(job_info, indent=2))

        # Download all WARC files.
        tmpdir = tempfile.mkdtemp(prefix="kalika-")
        tmppath = Path(tmpdir)
        self.api.retrieve_warcs(job_name=job_name, local_folderpath=tmppath)
        warc_files = list(tmppath.glob("*.warc.gz"))
        # WEB-20260911001134873-00000-35~66ada044be25~8443.warc.gz
        # WEB-20260911003631649-00001-35~66ada044be25~8443.warc.gz
        # WEB-20260911005933868-00002-35~66ada044be25~8443.warc.gz
        if warc_files:
            if len(warc_files) >= 2:
                regex = re.compile(r"WEB-\d+?-(.+?)-.*\.warc\.gz")
                for warc_file in warc_files:
                    m = regex.match(str(warc_file.name))
                    if m:
                        seq_number = m.group(1)
                        warc_file.move(target_path / f"{job_name}-{seq_number}.warc.gz")  # ty: ignore[unresolved-attribute]
                    else:
                        raise ValueError(
                            f"Could not parse WARC file name {warc_file.name}"
                        )
            else:
                warc_file = warc_files[0]
                logger.info("INFO: WARC file for %s: %s", job_name, warc_file)
                warc_file.move(target_path / f"{job_name}.warc.gz")  # ty: ignore[unresolved-attribute]

            self.api.teardown(job_name=job_name)
            # api.wait_for_action(job_name=job_name, action="teardown", poll_delay=0.25)
            # time.sleep(1)
            # api.delete_job_dir(job_name=job_name)
        else:
            logger.info("WARNING: No WARC files for: %s", job_name)
        shutil.rmtree(tmpdir)
