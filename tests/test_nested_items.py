from __future__ import annotations

import unittest
from typing import Any

from itemloaders import ItemLoader


class NestedItemTest(unittest.TestCase):
    """Test that adding items as values works as expected."""

    def _test_item(self, item: Any) -> None:
        il = ItemLoader()
        il.add_value("item_list", item)
        self.assertEqual(il.load_item(), {"item_list": [item]})

    def test_attrs(self):
        try:
            import attr  # noqa: PLC0415
        except ImportError:
            self.skipTest("Cannot import attr")

        @attr.s
        class TestItem:
            foo = attr.ib()

        self._test_item(TestItem(foo="bar"))

    def test_dataclass(self):
        try:
            from dataclasses import dataclass  # noqa: PLC0415
        except ImportError:
            self.skipTest("Cannot import dataclasses.dataclass")

        @dataclass
        class TestItem:
            foo: str

        self._test_item(TestItem(foo="bar"))

    def test_dict(self):
        self._test_item({"foo": "bar"})

    def test_scrapy_item(self):
        try:
            from scrapy import Field, Item  # noqa: PLC0415
        except ImportError:
            self.skipTest("Cannot import Field or Item from scrapy")

        class TestItem(Item):
            foo = Field()

        self._test_item(TestItem(foo="bar"))
