from kalika.heritrix import Crawler


def test_dummy():
    assert 42 == 42


def test_import():
    crawler = Crawler(None)  # ty: ignore[invalid-argument-type]
    assert crawler.api is not None
