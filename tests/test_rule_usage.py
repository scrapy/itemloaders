from collections import Counter

import pytest
from parsel import Selector

from itemloaders import ItemLoader


class Stats:
    def __init__(self) -> None:
        self.values: Counter[str] = Counter()

    def inc_value(self, key: str, count: int = 1) -> None:
        self.values[key] += count


@pytest.fixture
def stats():
    return Stats()


@pytest.fixture
def loader(stats):
    selector = Selector(
        text='<html><header><h1>Color TV</h1></header><p id="price">$1200</p></html>'
    )
    return ItemLoader(selector=selector, stats=stats)


def test_css(loader, stats):
    loader.add_css("name", ["h1::text", 'meta[name="title"]::attr(content)'])
    assert stats.values == {
        "parser/name/css/h1::text": 1,
        'parser/name/css/meta[name="title"]::attr(content)': 0,
    }


def test_xpath(loader, stats):
    loader.replace_xpath("name", "//h1/text()")
    assert stats.values == {"parser/name/xpath///h1/text()": 1}


def test_jmes(stats):
    loader = ItemLoader(selector=Selector(text='{"name": "Color TV"}'), stats=stats)
    loader.add_jmes("name", "name")
    loader.add_jmes("name", "title")
    assert stats.values == {
        "parser/name/jmes/name": 1,
        "parser/name/jmes/title": 0,
    }


def test_no_field_name(loader, stats):
    assert loader.get_css("h1::text") == ["Color TV"]
    assert stats.values == {"parser/<none>/css/h1::text": 1}


def test_no_stats():
    loader = ItemLoader(selector=Selector(text="<h1>Color TV</h1>"))
    loader.add_css("name", "h1::text")
    assert loader.get_output_value("name") == ["Color TV"]


def test_nested_loader(loader, stats):
    loader.nested_css("header").add_css("name", "h1::text")
    assert stats.values == {"parser/name/css/h1::text": 1}


def test_repeated_rule(loader, stats):
    loader.add_css("name", "h1::text")
    loader.add_css("name", "h1::text")
    assert stats.values == {"parser/name/css/h1::text": 2}
