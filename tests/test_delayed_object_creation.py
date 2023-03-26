from collections.abc import MutableMapping
from unittest import TestCase

from parsel import Selector

from itemloaders import ItemLoader


EXPECTED_ERROR = RuntimeError


class UninitializableItem(dict):

    def __init__(self, *args, **kwargs):
        raise EXPECTED_ERROR


class UninitializableItemLoader(ItemLoader):
    default_item_class = UninitializableItem


class DelayedObjectCreationTestCase(TestCase):

    def test_loader_creation(self):
        UninitializableItemLoader()

    def test_add(self):
        selector = Selector(text="<html><body></body></html>")
        il = UninitializableItemLoader(selector=selector)
        il.add_value('key', 'value')
        il.add_css('key', 'html')
        il.add_xpath('key', '//html')

    def test_context(self):
        il = UninitializableItemLoader()
        context = il.context
        with self.assertRaises(EXPECTED_ERROR):
            context['item']

    def test_load_item(self):
        il = UninitializableItemLoader()
        with self.assertRaises(EXPECTED_ERROR):
            il.load_item()

    def test_nested_loader_creation(self):
        selector = Selector(text="<html><body></body></html>")
        il = UninitializableItemLoader(selector=selector)
        il.nested_css('html')
        il.nested_xpath('//html')

    def test_nested_load_item(self):
        selector = Selector(text="<html><body></body></html>")
        il = UninitializableItemLoader(selector=selector)

        css_il = il.nested_css('html')
        with self.assertRaises(EXPECTED_ERROR):
            css_il.load_item()

        xpath_il = il.nested_xpath('//html')
        with self.assertRaises(EXPECTED_ERROR):
            xpath_il.load_item()
