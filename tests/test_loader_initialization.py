import unittest
from typing import Any, Protocol

from itemloaders import ItemLoader


class InitializationTestProtocol(Protocol):
    item_class: Any

    def assertEqual(self, first: Any, second: Any, msg: Any = ...) -> None: ...

    def assertIsInstance(self, obj: object, cls: type, msg: Any = None) -> None: ...


class InitializationTestMixin:
    item_class: Any = None

    def test_keep_single_value(self: InitializationTestProtocol) -> None:
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {"name": ["foo"]})

    def test_keep_list(self: InitializationTestProtocol) -> None:
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {"name": ["foo", "bar"]})

    def test_add_value_singlevalue_singlevalue(
        self: InitializationTestProtocol,
    ) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        il.add_value("name", "bar")
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {"name": ["foo", "bar"]})

    def test_add_value_singlevalue_list(self: InitializationTestProtocol) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        il.add_value("name", ["item", "loader"])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {"name": ["foo", "item", "loader"]})

    def test_add_value_list_singlevalue(self: InitializationTestProtocol) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        il.add_value("name", "qwerty")
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {"name": ["foo", "bar", "qwerty"]})

    def test_add_value_list_list(self: InitializationTestProtocol) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        il.add_value("name", ["item", "loader"])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {"name": ["foo", "bar", "item", "loader"]})

    def test_get_output_value_singlevalue(self: InitializationTestProtocol) -> None:
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        self.assertEqual(il.get_output_value("name"), ["foo"])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(loaded_item, {"name": ["foo"]})

    def test_get_output_value_list(self: InitializationTestProtocol) -> None:
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        self.assertEqual(il.get_output_value("name"), ["foo", "bar"])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(loaded_item, {"name": ["foo", "bar"]})

    def test_values_single(self: InitializationTestProtocol) -> None:
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        self.assertEqual(il._values.get("name"), ["foo"])

    def test_values_list(self: InitializationTestProtocol) -> None:
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        self.assertEqual(il._values.get("name"), ["foo", "bar"])


class InitializationFromDictTest(InitializationTestMixin, unittest.TestCase):
    item_class = dict
