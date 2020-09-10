import unittest

from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst


class InitializationTestMixin:

    item_class = None

    def test_keep_single_value(self):
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo']})

    def test_keep_list(self):
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar']})

    def test_add_value_singlevalue_singlevalue(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        il.add_value('name', 'bar')
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar']})

    def test_add_value_singlevalue_list(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        il.add_value('name', ['item', 'loader'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'item', 'loader']})

    def test_add_value_list_singlevalue(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        il.add_value('name', 'qwerty')
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar', 'qwerty']})

    def test_add_value_list_list(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        il.add_value('name', ['item', 'loader'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar', 'item', 'loader']})

    def test_get_output_value_singlevalue(self):
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        self.assertEqual(il.get_output_value('name'), ['foo'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(loaded_item, dict({'name': ['foo']}))

    def test_get_output_value_list(self):
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        self.assertEqual(il.get_output_value('name'), ['foo', 'bar'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(loaded_item, dict({'name': ['foo', 'bar']}))

    def test_get_output_value_default_singlevalue(self):
        """
        The default value should be used only when the returned value is
        empty (None, '', etc.) and there is a default value defined
        """
        input_item = self.item_class()
        il = ItemLoader(item=input_item)
        il.default_output_processor = TakeFirst()  # make "name" field single

        self.assertEqual(il.get_output_value('name'), None)
        self.assertEqual(il.get_output_value('name', ''), '')
        self.assertEqual(il.get_output_value('name', []), [])
        self.assertEqual(il.get_output_value('name', 'foo'), 'foo')

        il.add_value('name', '')
        self.assertEqual(il.get_output_value('name'), None)
        self.assertEqual(il.get_output_value('name', ''), '')
        self.assertEqual(il.get_output_value('name', []), [])
        self.assertEqual(il.get_output_value('name', 'foo'), 'foo')
        self.assertEqual(il.load_item(), {})

        input_item2 = self.item_class()
        il2 = ItemLoader(item=input_item2)
        il2.default_output_processor = TakeFirst()
        il2.add_value('name', 'foo')
        self.assertEqual(il2.get_output_value('name'), 'foo')
        self.assertEqual(il2.get_output_value('name', 'bar'), 'foo')
        self.assertEqual(il2.load_item(), dict({'name': 'foo'}))

    def test_get_output_value_default_list(self):
        """
        The default value should be used only when the returned value is
        empty ([], etc.) and there is a default value defined
        """
        input_item = self.item_class()
        il = ItemLoader(item=input_item)
        il.add_value('name', [])
        self.assertEqual(il.get_output_value('name'), [])
        self.assertEqual(il.get_output_value('name', 'foo'), 'foo')
        self.assertEqual(il.load_item(), {})

        input_item2 = self.item_class()
        il2 = ItemLoader(item=input_item2)
        il2.add_value('name', ['foo', 'bar'])
        self.assertEqual(il2.get_output_value('name'), ['foo', 'bar'])
        self.assertEqual(il2.get_output_value('name', ['spam']), ['foo', 'bar'])
        self.assertEqual(il2.load_item(), dict({'name': ['foo', 'bar']}))

    def test_values_single(self):
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        self.assertEqual(il._values.get('name'), ['foo'])

    def test_values_list(self):
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        self.assertEqual(il._values.get('name'), ['foo', 'bar'])


class InitializationFromDictTest(InitializationTestMixin, unittest.TestCase):
    item_class = dict
