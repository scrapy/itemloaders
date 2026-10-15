from __future__ import annotations

from typing import Any

import pytest
from parsel import Selector

from itemloaders import ItemLoader

EXPECTED_ERROR = RuntimeError


class UninitializableItem(dict[str, Any]):
    def __init__(self, *args: Any, **kwargs: Any):
        raise EXPECTED_ERROR


class UninitializableItemLoader(ItemLoader):
    default_item_class = UninitializableItem


def test_loader_creation():
    UninitializableItemLoader()


def test_add():
    selector = Selector(text="<html><body></body></html>")
    il = UninitializableItemLoader(selector=selector)
    il.add_value("key", "value")
    il.add_css("key", "html")
    il.add_xpath("key", "//html")


def test_context():
    il = UninitializableItemLoader()
    with pytest.raises(EXPECTED_ERROR):
        _ = il.context["item"]


def test_load_item():
    il = UninitializableItemLoader()
    with pytest.raises(EXPECTED_ERROR):
        il.load_item()


def test_nested_loader_creation():
    selector = Selector(text="<html><body></body></html>")
    il = UninitializableItemLoader(selector=selector)
    il.nested_css("html")
    il.nested_xpath("//html")


def test_nested_load_item():
    selector = Selector(text="<html><body></body></html>")
    il = UninitializableItemLoader(selector=selector)

    css_il = il.nested_css("html")
    with pytest.raises(EXPECTED_ERROR):
        css_il.load_item()

    xpath_il = il.nested_xpath("//html")
    with pytest.raises(EXPECTED_ERROR):
        xpath_il.load_item()
