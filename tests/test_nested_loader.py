import unittest

from parsel import Selector

from itemloaders import ItemLoader


class SubselectorLoaderTest(unittest.TestCase):
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

        self.assertEqual(loader.get_output_value("name"), ["marta"])
        self.assertEqual(
            loader.get_output_value("name_div"), ['<div id="id">marta</div>']
        )
        self.assertEqual(loader.get_output_value("name_value"), ["marta"])

        self.assertEqual(loader.get_output_value("name"), nl.get_output_value("name"))
        self.assertEqual(
            loader.get_output_value("name_div"), nl.get_output_value("name_div")
        )
        self.assertEqual(
            loader.get_output_value("name_value"), nl.get_output_value("name_value")
        )

    def test_nested_css(self):
        loader = ItemLoader(selector=self.selector)
        nl = loader.nested_css("header")
        nl.add_xpath("name", "div/text()")
        nl.add_css("name_div", "#id")
        assert nl.selector
        nl.add_value("name_value", nl.selector.xpath('div[@id = "id"]/text()').getall())

        self.assertEqual(loader.get_output_value("name"), ["marta"])
        self.assertEqual(
            loader.get_output_value("name_div"), ['<div id="id">marta</div>']
        )
        self.assertEqual(loader.get_output_value("name_value"), ["marta"])

        self.assertEqual(loader.get_output_value("name"), nl.get_output_value("name"))
        self.assertEqual(
            loader.get_output_value("name_div"), nl.get_output_value("name_div")
        )
        self.assertEqual(
            loader.get_output_value("name_value"), nl.get_output_value("name_value")
        )

    def test_nested_replace(self):
        loader = ItemLoader(selector=self.selector)
        nl1 = loader.nested_xpath("//footer")
        nl2 = nl1.nested_xpath("a")

        loader.add_xpath("url", "//footer/a/@href")
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])
        nl1.replace_xpath("url", "img/@src")
        self.assertEqual(loader.get_output_value("url"), ["/images/logo.png"])
        nl2.replace_xpath("url", "@href")
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])

    def test_nested_ordering(self):
        loader = ItemLoader(selector=self.selector)
        nl1 = loader.nested_xpath("//footer")
        nl2 = nl1.nested_xpath("a")

        nl1.add_xpath("url", "img/@src")
        loader.add_xpath("url", "//footer/a/@href")
        nl2.add_xpath("url", "text()")
        loader.add_xpath("url", "//footer/a/@href")

        self.assertEqual(
            loader.get_output_value("url"),
            [
                "/images/logo.png",
                "http://www.scrapy.org",
                "homepage",
                "http://www.scrapy.org",
            ],
        )

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

        self.assertEqual(item["name"], ["marta"])
        self.assertEqual(item["url"], ["http://www.scrapy.org"])
        self.assertEqual(item["image"], ["/images/logo.png"])

    def test_nested_empty_selector(self):
        loader = ItemLoader(selector=self.selector)
        nested_xpath = loader.nested_xpath("//bar")
        assert isinstance(nested_xpath, ItemLoader)
        nested_xpath.add_xpath("foo", "./foo")

        nested_css = loader.nested_css("bar")
        assert isinstance(nested_css, ItemLoader)
        nested_css.add_css("foo", "foo")
