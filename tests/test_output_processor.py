import unittest

from itemloaders import ItemLoader
from itemloaders.processors import Identity, Compose, TakeFirst


def take_first(value):
    return value[0]


class TestOutputProcessor(unittest.TestCase):

    def test_item_class(self):

        class TempDict(dict):
            def __init__(self, *args, **kwargs):
                super(TempDict, self).__init__(self, *args, **kwargs)
                self.setdefault('temp', 0.3)

        class TempLoader(ItemLoader):
            default_item_class = TempDict
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        loader = TempLoader()
        item = loader.load_item()
        self.assertIsInstance(item, TempDict)
        self.assertEqual(dict(item), {'temp': 0.3})

    def test_item_object(self):

        class TempLoader(ItemLoader):
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        item = dict()
        item.setdefault('temp', 0.3)
        loader = TempLoader(item=item)
        item = loader.load_item()
        self.assertIsInstance(item, dict)
        self.assertEqual(dict(item), {'temp': 0.3})

    def test_unbound_processor(self):
        """Ensure that a processor not taking a `self` parameter does not break
        anything"""

        class TempLoader(ItemLoader):
            default_output_processor = take_first

        loader = TempLoader()
        loader.add_value('foo', 'bar')
        self.assertEqual(loader.load_item(), {'foo': 'bar'})
