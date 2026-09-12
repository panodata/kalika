# Kalika

## About

Kalika is a web archiver and crawler based on Heritrix and pywb.

- Crawl the web using Internet Archive's Heritrix to create per-site WARC files.
- Replay WARC files using pywb's `wayback` application, providing the traditional
  "Wayback Machine" functionality.

## Install

For running or installing the `kalika` Python package,
we are recommending to use [uv]. [^1][^2]
```shell
uvx kalika
```

Alternatively, if you like to install it account-wide on your system:
```shell
uv tool install kalika
```

[^1]: You can install `uv` using `pip install uv`, or another method that matches your operating system.
[^2]: While installing `kalika` with vanilla `pip` is possible, it is an order of magnitude slower.

## Project

### Contribute

Contributions are very much welcome. Please visit the [sandbox documentation]
to learn how to spin up a development environment on your workstation and submit
patches, or create a [ticket][Issues] to report a bug or propose a feature.

### Status

Breaking changes should be expected until a 1.0 release, so version pinning is
strongly recommended, especially when using this software as a library.
For example:
```shell
pip install 'kalika[full]==0.0.42'
```

### License

The project is licensed under the Apache 2.0 License, see the [LICENSE] file for details.

### Acknowledgements

This project would not have been possible without the amazing work by the
authors and contributors to [Heritrix], [pywb], and all the other great
software packages turtles all the way down. Kudos.

### Etymology

[Kalika][Kalika-goddess] is a major goddess in Hinduism, primarily associated
with time, death, and destruction. Kalika is also connected with transcendental
knowledge and is the first of the ten Mahavidyas, goddesses who provide
liberating knowledge.


[Heritrix]: https://github.com/internetarchive/heritrix3
[Issues]: https://github.com/panodata/kalika/issues
[Kalika-goddess]: https://en.wikipedia.org/wiki/Kali
[LICENSE]: https://github.com/panodata/kalika/blob/main/LICENSE
[pywb]: https://pypi.org/project/pywb/
[sandbox documentation]: https://kalika.readthedocs.io/sandbox.html
[uv]: https://docs.astral.sh/uv/
