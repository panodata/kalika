---
outline: deep
---

# Introduction

Kalika is a web archiver and crawler based on Heritrix and pywb.

- Crawl the web using Internet Archive's Heritrix to create per-site WARC files.
- Replay WARC files using pywb's `wayback` application, providing the traditional
  "Wayback Machine" functionality.

## Installation

We recommend using [uv] to run `kalika`.

```bash
pip install uv
uvx kalika
```

Alternatively, if you'd like to install Kalika globally:

```bash
uv pip install --system kalika
```

While installation with vanilla `pip` is possible, it is an order of magnitude slower.

### License

The project is licensed under the Apache 2.0 License, see the [LICENSE] file for details.

### Acknowledgements

This project would not have been possible without the amazing work by the
authors and contributors to [Heritrix], [pywb], and all the other great
software packages turtles all the way down. Kudos.

```{toctree}
:caption: Project
:maxdepth: 1
:hidden:

sandbox
changelog
backlog
```


[Heritrix]: https://github.com/internetarchive/heritrix3
[LICENSE]: https://github.com/panodata/kalika/blob/main/LICENSE
[pywb]: https://pypi.org/project/pywb/
[uv]: https://github.com/astral-sh/uv
