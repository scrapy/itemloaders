from collections.abc import MutableMapping
from unittest import TestCase

from parsel import Selector

from itemloaders import ItemLoader


class UninitializableItem(MutableMapping):
    """Cannot be initialized due to undefined abstract methods, raises
    TypeError during initialization."""
    pass


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
        with self.assertRaises(TypeError):
            context['item']

    def test_load_item(self):
        il = UninitializableItemLoader()
        with self.assertRaises(TypeError):
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
        with self.assertRaises(TypeError):
            css_il.load_item()

        xpath_il = il.nested_xpath('//html')
        with self.assertRaises(TypeError):
            xpath_il.load_item()
