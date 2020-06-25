import unittest
from typing import Optional
import sys

import pytest

from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst


if sys.version_info < (3, 7):
    pytestmark = pytest.mark.skip('@dataclass is only supported in pytho 3.7+')
else:
    from dataclasses import dataclass, field


class DataclassItemLoaderTest(unittest.TestCase):

    def test_raise_exception_if_dataclass_requires_arguments(self):

        @dataclass
        class Product:
            name: str
            price: float

        class ProductLoader(ItemLoader):
            default_item_class = Product
            default_output_processor = TakeFirst()

        with pytest.raises(TypeError) as einfo:
            ProductLoader()

        assert einfo.value.args[0] == (
            'Currently, ItemLoader requires default_item_class '
            'to be a callable with no arguments. '
            'For more information, visit the API Reference in the Documentation.'
        )

    def test_dataclass_no_arguments(self):

        @dataclass
        class Product:
            name: Optional[str] = field(default=None)
            price: Optional[float] = field(default=None)

        class ProductLoader(ItemLoader):
            default_item_class = Product
            default_output_processor = TakeFirst()

        loader = ProductLoader()
        loader.add_value('name', 'test 1')
        loader.add_value('price', 9.65)
        item = loader.load_item()

        assert item.name == 'test 1'
        assert item.price == 9.65
