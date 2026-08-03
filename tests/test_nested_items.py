from __future__ import annotations

from typing import Any

import pytest

from itemloaders import ItemLoader


def _test_item(item: Any) -> None:
    il = ItemLoader()
    il.add_value("item_list", item)
    assert il.load_item() == {"item_list": [item]}


def test_attrs():
    try:
        import attr  # noqa: PLC0415
    except ImportError:
        pytest.skip("Cannot import attr")

    @attr.s
    class TestItem:
        foo = attr.ib()

    _test_item(TestItem(foo="bar"))


def test_dataclass():
    try:
        from dataclasses import dataclass  # noqa: PLC0415
    except ImportError:
        pytest.skip("Cannot import dataclasses.dataclass")

    @dataclass
    class TestItem:
        foo: str

    _test_item(TestItem(foo="bar"))


def test_dict():
    _test_item({"foo": "bar"})


def test_scrapy_item():
    try:
        from scrapy import Field, Item  # noqa: PLC0415
    except ImportError:
        pytest.skip("Cannot import Field or Item from scrapy")

    class TestItem(Item):
        foo = Field()

    _test_item(TestItem(foo="bar"))
