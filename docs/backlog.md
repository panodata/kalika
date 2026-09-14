# Backlog

## Iteration +1

- Service: Parse JSON reports to find unfinished jobs
- Image snapshot of homepage using [shot-scraper]

## Iteration +2

- Searching/Indexing: Connect [warcio] to [paperless-ngx], [openaleph-client] and/or [ftmq]
- Recycle Heritrix workers after processing 500 jobs,
  or after accumulating X GB in its spool directory
- Define per-job limits (1 h, 10000 documents) in TOML configuration
- Needs future-looking bookkeeping to get "add to preferred server" right,
  because "add" is a slow operation

## Iteration +3

- Report: Heritrix has concurrency flaws, see ...
- `api.delete_job_dir` raises an exception


[ftmq]: https://github.com/dataresearchcenter/ftmq
[openaleph-client]: https://github.com/dataresearchcenter/opal-client
[paperless-ngx]: https://paperless-ngx.com/
[shot-scraper]: https://shot-scraper.datasette.io/
[warcio]: https://github.com/webrecorder/warcio
