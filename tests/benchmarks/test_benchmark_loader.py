from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from parsel import Selector

from itemloaders import ItemLoader
from itemloaders.processors import Identity, Join, MapCompose, TakeFirst

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture

SELECTOR = Selector(
    text="""
    <html>
    <body>
        <h1 class="name"> a product name </h1>
        <div id="description">
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
        </div>
        <ul class="tags">
            <li>foo</li><li>bar</li><li>baz</li>
        </ul>
        <a class="url" href="http://www.example.com/product">Product</a>
        <span class="price">42.50</span>
    </body>
    </html>
    """
)

NAMES = [f" product {index} " for index in range(50)]


@dataclass
class Seller:
    name: str


class ProductLoader(ItemLoader):
    default_output_processor = TakeFirst()

    name_in = MapCompose(str.strip, str.title)
    description_out = Join()
    tags_out = Identity()
    price_in = MapCompose(str.strip, float)


def strip_with_context(value: str, loader_context: dict[str, Any]) -> str:
    return value.strip(loader_context.get("chars"))


class ContextProductLoader(ProductLoader):
    name_in = MapCompose(strip_with_context, str.title)


class DynamicProductLoader(ProductLoader):
    """Loader that builds its processors per instance, so that every item gets
    a different processor object."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.name_in = MapCompose(str.strip, self.title)

    def title(self, value: str) -> str:
        return value.title()


def test_selector(benchmark: BenchmarkFixture) -> None:
    """Load an item out of a page, the way a spider callback does."""

    @benchmark
    def factory() -> None:
        loader = ProductLoader(selector=SELECTOR)
        loader.add_css("name", "h1.name::text")
        loader.add_css("description", "#description p::text")
        loader.add_css("tags", "ul.tags li::text")
        loader.add_xpath("url", "//a[@class='url']/@href")
        loader.add_css("price", "span.price::text")
        loader.load_item()


def test_values(benchmark: BenchmarkFixture) -> None:
    """Load an item out of already extracted values."""

    @benchmark
    def factory() -> None:
        loader = ProductLoader()
        loader.add_value("name", " a product name ")
        loader.add_value("description", ["First paragraph.", "Second paragraph."])
        loader.add_value("tags", ["foo", "bar", "baz"])
        loader.add_value("url", "http://www.example.com/product")
        loader.add_value("price", "42.50")
        loader.load_item()


def test_many_values(benchmark: BenchmarkFixture) -> None:
    """Load a field with as many values as a listing page can yield."""

    @benchmark
    def factory() -> None:
        loader = ProductLoader()
        loader.add_value("name", NAMES)
        loader.load_item()


def test_loader_context(benchmark: BenchmarkFixture) -> None:
    """Load a field whose processor takes the loader context."""

    @benchmark
    def factory() -> None:
        loader = ContextProductLoader()
        loader.add_value("name", NAMES)
        loader.load_item()


def test_dynamic_processors(benchmark: BenchmarkFixture) -> None:
    """Load a field whose processors are built per loader instance."""

    @benchmark
    def factory() -> None:
        loader = DynamicProductLoader()
        loader.add_value("name", NAMES)
        loader.load_item()


def test_nested_items(benchmark: BenchmarkFixture) -> None:
    """Load an item that has other items among its values."""

    @benchmark
    def factory() -> None:
        loader = ItemLoader()
        loader.add_value("url", "http://www.example.com/product")
        loader.add_value("brand", {"name": "Foo", "url": "http://www.example.com/foo"})
        loader.add_value("seller", Seller(name="Bar"))
        loader.load_item()
