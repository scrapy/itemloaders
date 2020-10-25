import unittest
from dataclasses import dataclass

from itemloaders import ItemLoader as BaseItemLoader
from itemloaders.processors import Identity


class ItemLoader(BaseItemLoader):
    item_list_in = Identity()
    item_list_out = Identity()


class NestedItemTest(unittest.TestCase):
    """Test that adding items as values works as expected."""

    def test_attrs(self):
        try:
            import attr
        except ImportError:
            self.skipTest("Cannot import attr")

        @attr.s
        class TestItem:
            foo = attr.ib()

        item = TestItem(foo='bar')
        il = ItemLoader()
        il.add_value('item_list', item)
        self.assertEqual(il.load_item(), {'item_list': [item]})

    def test_dataclass(self):
        @dataclass
        class TestItem:
            foo: str

        item = TestItem(foo='bar')
        il = ItemLoader()
        il.add_value('item_list', item)
        self.assertEqual(il.load_item(), {'item_list': [item]})

    def test_dict(self):
        item = {'foo': 'bar'}
        il = ItemLoader()
        il.add_value('item_list', item)
        self.assertEqual(il.load_item(), {'item_list': [item]})

    def test_scrapy_item(self):
        try:
            from scrapy import Field, Item
        except ImportError:
            self.skipTest("Cannot import Field or Item from scrapy")

        class TestItem(Item):
            foo = Field()

        item = TestItem(foo='bar')
        il = ItemLoader()
        il.add_value('item_list', item)
        self.assertEqual(il.load_item(), {'item_list': [item]})
