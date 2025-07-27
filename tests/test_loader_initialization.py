from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from itemloaders import ItemLoader


class TestInitializationBase(ABC):
    @property
    @abstractmethod
    def item_class(self) -> type[Any]:
        raise NotImplementedError

    def test_keep_single_value(self) -> None:
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert dict(loaded_item) == {"name": ["foo"]}

    def test_keep_list(self) -> None:
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert dict(loaded_item) == {"name": ["foo", "bar"]}

    def test_add_value_singlevalue_singlevalue(
        self,
    ) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        il.add_value("name", "bar")
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert dict(loaded_item) == {"name": ["foo", "bar"]}

    def test_add_value_singlevalue_list(self) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        il.add_value("name", ["item", "loader"])
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert dict(loaded_item) == {"name": ["foo", "item", "loader"]}

    def test_add_value_list_singlevalue(self) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        il.add_value("name", "qwerty")
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert dict(loaded_item) == {"name": ["foo", "bar", "qwerty"]}

    def test_add_value_list_list(self) -> None:
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        il.add_value("name", ["item", "loader"])
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert dict(loaded_item) == {"name": ["foo", "bar", "item", "loader"]}

    def test_get_output_value_singlevalue(self) -> None:
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        assert il.get_output_value("name") == ["foo"]
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert loaded_item == {"name": ["foo"]}

    def test_get_output_value_list(self) -> None:
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        assert il.get_output_value("name") == ["foo", "bar"]
        loaded_item = il.load_item()
        assert isinstance(loaded_item, self.item_class)
        assert loaded_item == {"name": ["foo", "bar"]}

    def test_values_single(self) -> None:
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name="foo")
        il = ItemLoader(item=input_item)
        assert il._values.get("name") == ["foo"]

    def test_values_list(self) -> None:
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name=["foo", "bar"])
        il = ItemLoader(item=input_item)
        assert il._values.get("name") == ["foo", "bar"]


class InitializationFromDictTest(TestInitializationBase):
    item_class = dict
