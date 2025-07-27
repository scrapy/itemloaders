from __future__ import annotations

from typing import Any

from itemloaders import ItemLoader
from itemloaders.processors import Compose, Identity, TakeFirst


class TestOutputProcessorDict:
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
        assert isinstance(item, TempDict)
        assert dict(item) == {"temp": 0.3}


class TestOutputProcessorItem:
    def test_output_processor(self):
        class TempLoader(ItemLoader):
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        item: dict[str, Any] = {}
        item.setdefault("temp", 0.3)
        loader = TempLoader(item=item)
        item = loader.load_item()
        assert isinstance(item, dict)
        assert dict(item) == {"temp": 0.3}
