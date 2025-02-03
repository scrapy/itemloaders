from __future__ import annotations

import unittest
from typing import Any

from itemloaders import ItemLoader
from itemloaders.processors import Compose, Identity, TakeFirst


class TestOutputProcessorDict(unittest.TestCase):
    def test_output_processor(self):
        class TempDict(dict[str, Any]):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setdefault("temp", 0.3)

        class TempLoader(ItemLoader):
            default_item_class = TempDict
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        loader = TempLoader()
        item = loader.load_item()
        self.assertIsInstance(item, TempDict)
        self.assertEqual(dict(item), {"temp": 0.3})


class TestOutputProcessorItem(unittest.TestCase):
    def test_output_processor(self):
        class TempLoader(ItemLoader):
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        item: dict[str, Any] = {}
        item.setdefault("temp", 0.3)
        loader = TempLoader(item=item)
        item = loader.load_item()
        self.assertIsInstance(item, dict)
        self.assertEqual(dict(item), {"temp": 0.3})
