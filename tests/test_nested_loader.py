import pytest
from parsel import Selector

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose


class TestSubselectorLoader:
    selector = Selector(
        text="""
    <html>
    <body>
    <header>
      <div id="id">marta</div>
      <p>paragraph</p>
    </header>
    <footer class="footer">
      <a href="http://www.scrapy.org">homepage</a>
      <img src="/images/logo.png" width="244" height="65" alt="Scrapy">
    </footer>
    </body>
    </html>
    """
    )

    def test_nested_xpath(self):
        loader = ItemLoader(selector=self.selector)
        nl = loader.nested_xpath("//header")
        nl.add_xpath("name", "div/text()")
        nl.add_css("name_div", "#id")
        assert nl.selector
        nl.add_value("name_value", nl.selector.xpath('div[@id = "id"]/text()').getall())

        assert loader.get_output_value("name") == ["marta"]
        assert loader.get_output_value("name_div") == ['<div id="id">marta</div>']
        assert loader.get_output_value("name_value") == ["marta"]

        assert loader.get_output_value("name") == nl.get_output_value("name")
        assert loader.get_output_value("name_div") == nl.get_output_value("name_div")
        assert loader.get_output_value("name_value") == nl.get_output_value(
            "name_value"
        )

    def test_nested_css(self):
        loader = ItemLoader(selector=self.selector)
        nl = loader.nested_css("header")
        nl.add_xpath("name", "div/text()")
        nl.add_css("name_div", "#id")
        assert nl.selector
        nl.add_value("name_value", nl.selector.xpath('div[@id = "id"]/text()').getall())

        assert loader.get_output_value("name") == ["marta"]
        assert loader.get_output_value("name_div") == ['<div id="id">marta</div>']
        assert loader.get_output_value("name_value") == ["marta"]

        assert loader.get_output_value("name") == nl.get_output_value("name")
        assert loader.get_output_value("name_div") == nl.get_output_value("name_div")
        assert loader.get_output_value("name_value") == nl.get_output_value(
            "name_value"
        )

    def test_nested_replace(self):
        loader = ItemLoader(selector=self.selector)
        nl1 = loader.nested_xpath("//footer")
        nl2 = nl1.nested_xpath("a")

        loader.add_xpath("url", "//footer/a/@href")
        assert loader.get_output_value("url") == ["http://www.scrapy.org"]
        nl1.replace_xpath("url", "img/@src")
        assert loader.get_output_value("url") == ["/images/logo.png"]
        nl2.replace_xpath("url", "@href")
        assert loader.get_output_value("url") == ["http://www.scrapy.org"]

    def test_nested_ordering(self):
        loader = ItemLoader(selector=self.selector)
        nl1 = loader.nested_xpath("//footer")
        nl2 = nl1.nested_xpath("a")

        nl1.add_xpath("url", "img/@src")
        loader.add_xpath("url", "//footer/a/@href")
        nl2.add_xpath("url", "text()")
        loader.add_xpath("url", "//footer/a/@href")

        assert loader.get_output_value("url") == [
            "/images/logo.png",
            "http://www.scrapy.org",
            "homepage",
            "http://www.scrapy.org",
        ]

    def test_nested_load_item(self):
        loader = ItemLoader(selector=self.selector)
        nl1 = loader.nested_xpath("//footer")
        nl2 = nl1.nested_xpath("img")

        loader.add_xpath("name", "//header/div/text()")
        nl1.add_xpath("url", "a/@href")
        nl2.add_xpath("image", "@src")

        item = loader.load_item()

        assert item is loader.item
        assert item is nl1.item
        assert item is nl2.item

        assert item["name"] == ["marta"]
        assert item["url"] == ["http://www.scrapy.org"]
        assert item["image"] == ["/images/logo.png"]

    def test_nested_from_item(self):
        """Check that everything works as usual when the nested selector has a
        parent item"""
        item = {"foo": "bar"}
        loader = ItemLoader(selector=self.selector, item=item)
        nl1 = loader.nested_xpath("//footer")
        nl2 = nl1.nested_xpath("img")

        loader.add_xpath("name", "//header/div/text()")
        nl1.add_xpath("url", "a/@href")
        nl2.add_xpath("image", "@src")

        item = loader.load_item()

        assert item is loader.item
        assert item is nl1.item
        assert item is nl2.item

        assert item["foo"] == ["bar"]
        assert item["name"] == ["marta"]
        assert item["url"] == ["http://www.scrapy.org"]
        assert item["image"] == ["/images/logo.png"]

    def test_nested_empty_selector(self):
        loader = ItemLoader(selector=self.selector)
        nested_xpath = loader.nested_xpath("//bar")
        assert isinstance(nested_xpath, ItemLoader)
        nested_xpath.add_xpath("foo", "./foo")

        nested_css = loader.nested_css("bar")
        assert isinstance(nested_css, ItemLoader)
        nested_css.add_css("foo", "foo")


@pytest.mark.parametrize(
    ("method", "expression"), [("nested_xpath", "//footer"), ("nested_css", "footer")]
)
def test_nested_context_inheritance(method: str, expression: str) -> None:
    marker = object()
    loader = ItemLoader(
        selector=TestSubselectorLoader.selector, marker=marker, prefix="parent"
    )
    original_context = dict(loader.context)
    child = getattr(loader, method)(expression, prefix="child")
    sibling = getattr(loader, method)(expression)
    grandchild = child.nested_css("a")
    for nested in (child, sibling, grandchild):
        assert nested.context["marker"] is marker
        assert nested.context["item"] is loader.item
        assert nested.context["selector"] is nested.selector
        assert nested.context is not loader.context
    assert child.context["prefix"] == grandchild.context["prefix"] == "child"
    assert sibling.context["prefix"] == "parent"
    assert loader.context == original_context
    child.context["new"] = True
    assert "new" not in loader.context
    assert "new" not in sibling.context

    grandchild.default_input_processor = MapCompose(
        lambda value, loader_context: loader_context["prefix"] + ":" + value
    )
    grandchild.add_css("name", "::text")
    assert loader.load_item()["name"] == ["child:homepage"]


@pytest.mark.parametrize(
    ("method", "expression"), [("nested_xpath", "//div"), ("nested_css", "div")]
)
def test_nested_scrapy_response_context(method: str, expression: str) -> None:
    scrapy_loader = pytest.importorskip("scrapy.loader")
    scrapy_http = pytest.importorskip("scrapy.http")
    response = scrapy_http.HtmlResponse(
        url="https://example.com/", body=b'<div><a href="/target">link</a></div>'
    )
    loader = scrapy_loader.ItemLoader(item={}, response=response)
    nested = getattr(loader, method)(expression)
    nested.default_input_processor = MapCompose(
        lambda value, loader_context: loader_context["response"].urljoin(value)
    )
    nested.add_css(method, "a::attr(href)")
    assert nested.context["response"] is response
    assert loader.load_item()[method] == ["https://example.com/target"]
