import re
import unittest
from unittest.mock import MagicMock

from parsel import Selector

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


class CustomItemLoader(ItemLoader):
    name_in = MapCompose(lambda v: v.title())


class SelectortemLoaderTest(unittest.TestCase):
    selector = Selector(
        text="""
    <html>
    <body>
    <div id="id">marta</div>
    <p>paragraph</p>
    <a href="http://www.scrapy.org">homepage</a>
    <img src="/images/logo.png" width="244" height="65" alt="Scrapy">
    </body>
    </html>
    """
    )

    jmes_selector = Selector(
        text="""
    {
      "name": "marta",
      "description": "paragraph",
      "website": {
        "url": "http://www.scrapy.org",
        "name": "homepage"
      },
      "logo": "/images/logo.png"
    }
    """
    )

    def test_init_method(self):
        loader = CustomItemLoader()
        self.assertEqual(loader.selector, None)

    def test_init_method_errors(self):
        loader = CustomItemLoader()
        self.assertRaises(RuntimeError, loader.add_xpath, "url", "//a/@href")
        self.assertRaises(RuntimeError, loader.replace_xpath, "url", "//a/@href")
        self.assertRaises(RuntimeError, loader.get_xpath, "//a/@href")
        self.assertRaises(RuntimeError, loader.add_css, "name", "#name::text")
        self.assertRaises(RuntimeError, loader.replace_css, "name", "#name::text")
        self.assertRaises(RuntimeError, loader.get_css, "#name::text")

    def test_init_method_with_selector(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)

        loader.add_xpath("name", "//div/text()")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])

    def test_init_method_with_selector_css(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)

        loader.add_css("name", "div::text")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])

        loader.add_css("url", "a::attr(href)")
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])

        # combining/accumulating CSS selectors and XPath expressions
        loader.add_xpath("name", "//div/text()")
        self.assertEqual(loader.get_output_value("name"), ["Marta", "Marta"])

        loader.add_xpath("url", "//img/@src")
        self.assertEqual(
            loader.get_output_value("url"),
            ["http://www.scrapy.org", "/images/logo.png"],
        )

    def test_add_xpath_re(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath("name", "//div/text()", re="ma")
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath("name", "//div/text()", re=re.compile("ma"))
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

    def test_add_xpath_variables(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath("name", "id($id)/text()", id="id")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath("name", "id($id)/text()", id="id2")
        self.assertEqual(loader.get_output_value("name"), [])

    def test_replace_xpath(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_xpath("name", "//div/text()")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_xpath("name", "//p/text()")
        self.assertEqual(loader.get_output_value("name"), ["Paragraph"])

        loader.replace_xpath("name", ["//p/text()", "//div/text()"])
        self.assertEqual(loader.get_output_value("name"), ["Paragraph", "Marta"])

    def test_get_xpath(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertEqual(loader.get_xpath("//p/text()"), ["paragraph"])
        self.assertEqual(loader.get_xpath("//p/text()", TakeFirst()), "paragraph")
        self.assertEqual(loader.get_xpath("//p/text()", TakeFirst(), re="pa"), "pa")

        self.assertEqual(
            loader.get_xpath(["//p/text()", "//div/text()"]), ["paragraph", "marta"]
        )

    def test_replace_xpath_multi_fields(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath(None, "//div/text()", TakeFirst(), lambda x: {"name": x})
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_xpath(None, "//p/text()", TakeFirst(), lambda x: {"name": x})
        self.assertEqual(loader.get_output_value("name"), ["Paragraph"])

    def test_replace_xpath_re(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_xpath("name", "//div/text()")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_xpath("name", "//div/text()", re="ma")
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

    def test_add_css_re(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_css("name", "div::text", re="ma")
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

        loader.add_css("url", "a::attr(href)", re="http://(.+)")
        self.assertEqual(loader.get_output_value("url"), ["www.scrapy.org"])

        loader = CustomItemLoader(selector=self.selector)
        loader.add_css("name", "div::text", re=re.compile("ma"))
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

        loader.add_css("url", "a::attr(href)", re=re.compile("http://(.+)"))
        self.assertEqual(loader.get_output_value("url"), ["www.scrapy.org"])

    def test_replace_css(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_css("name", "div::text")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_css("name", "p::text")
        self.assertEqual(loader.get_output_value("name"), ["Paragraph"])

        loader.replace_css("name", ["p::text", "div::text"])
        self.assertEqual(loader.get_output_value("name"), ["Paragraph", "Marta"])

        loader.add_css("url", "a::attr(href)", re="http://(.+)")
        self.assertEqual(loader.get_output_value("url"), ["www.scrapy.org"])
        loader.replace_css("url", "img::attr(src)")
        self.assertEqual(loader.get_output_value("url"), ["/images/logo.png"])

    def test_get_css(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertEqual(loader.get_css("p::text"), ["paragraph"])
        self.assertEqual(loader.get_css("p::text", TakeFirst()), "paragraph")
        self.assertEqual(loader.get_css("p::text", TakeFirst(), re="pa"), "pa")

        self.assertEqual(
            loader.get_css(["p::text", "div::text"]), ["paragraph", "marta"]
        )
        self.assertEqual(
            loader.get_css(["a::attr(href)", "img::attr(src)"]),
            ["http://www.scrapy.org", "/images/logo.png"],
        )

    def test_replace_css_multi_fields(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_css(None, "div::text", TakeFirst(), lambda x: {"name": x})
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_css(None, "p::text", TakeFirst(), lambda x: {"name": x})
        self.assertEqual(loader.get_output_value("name"), ["Paragraph"])

        loader.add_css(None, "a::attr(href)", TakeFirst(), lambda x: {"url": x})
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])
        loader.replace_css(None, "img::attr(src)", TakeFirst(), lambda x: {"url": x})
        self.assertEqual(loader.get_output_value("url"), ["/images/logo.png"])

    def test_replace_css_re(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_css("url", "a::attr(href)")
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])
        loader.replace_css("url", "a::attr(href)", re=r"http://www\.(.+)")
        self.assertEqual(loader.get_output_value("url"), ["scrapy.org"])

    def test_jmes_not_installed(self):
        selector = MagicMock(spec=Selector)
        del selector.jmespath
        loader = CustomItemLoader(selector=selector)
        with self.assertRaises(AttributeError) as err:
            loader.add_jmes("name", "name", re="ma")

        self.assertEqual(
            str(err.exception), "Please install parsel >= 1.8.1 to get jmespath support"
        )

    def test_add_jmes_re(self):
        loader = CustomItemLoader(selector=self.jmes_selector)
        loader.add_jmes("name", "name", re="ma")
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

        loader.add_jmes("url", "website.url", re="http://(.+)")
        self.assertEqual(loader.get_output_value("url"), ["www.scrapy.org"])

        loader = CustomItemLoader(selector=self.jmes_selector)
        loader.add_jmes("name", "name", re=re.compile("ma"))
        self.assertEqual(loader.get_output_value("name"), ["Ma"])

        loader.add_jmes("url", "website.url", re=re.compile("http://(.+)"))
        self.assertEqual(loader.get_output_value("url"), ["www.scrapy.org"])

    def test_get_jmes(self):
        loader = CustomItemLoader(selector=self.jmes_selector)
        self.assertEqual(loader.get_jmes("description"), ["paragraph"])
        self.assertEqual(loader.get_jmes("description", TakeFirst()), "paragraph")
        self.assertEqual(loader.get_jmes("description", TakeFirst(), re="pa"), "pa")

        self.assertEqual(
            loader.get_jmes(["description", "name"]), ["paragraph", "marta"]
        )
        self.assertEqual(
            loader.get_jmes(["website.url", "logo"]),
            ["http://www.scrapy.org", "/images/logo.png"],
        )

    def test_replace_jmes(self):
        loader = CustomItemLoader(selector=self.jmes_selector)
        self.assertTrue(loader.selector)
        loader.add_jmes("name", "name")
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_jmes("name", "description")
        self.assertEqual(loader.get_output_value("name"), ["Paragraph"])

        loader.replace_jmes("name", ["description", "name"])
        self.assertEqual(loader.get_output_value("name"), ["Paragraph", "Marta"])

        loader.add_jmes("url", "website.url", re="http://(.+)")
        self.assertEqual(loader.get_output_value("url"), ["www.scrapy.org"])
        loader.replace_jmes("url", "logo")
        self.assertEqual(loader.get_output_value("url"), ["/images/logo.png"])

    def test_replace_jmes_multi_fields(self):
        loader = CustomItemLoader(selector=self.jmes_selector)
        loader.add_jmes(None, "name", TakeFirst(), lambda x: {"name": x})
        self.assertEqual(loader.get_output_value("name"), ["Marta"])
        loader.replace_jmes(None, "description", TakeFirst(), lambda x: {"name": x})
        self.assertEqual(loader.get_output_value("name"), ["Paragraph"])

        loader.add_jmes(None, "website.url", TakeFirst(), lambda x: {"url": x})
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])
        loader.replace_jmes(None, "logo", TakeFirst(), lambda x: {"url": x})
        self.assertEqual(loader.get_output_value("url"), ["/images/logo.png"])

    def test_replace_jmes_re(self):
        loader = CustomItemLoader(selector=self.jmes_selector)
        self.assertTrue(loader.selector)
        loader.add_jmes("url", "website.url")
        self.assertEqual(loader.get_output_value("url"), ["http://www.scrapy.org"])
        loader.replace_jmes("url", "website.url", re=r"http://www\.(.+)")
        self.assertEqual(loader.get_output_value("url"), ["scrapy.org"])

    def test_fluent_interface(self):
        loader = ItemLoader(selector=self.selector)
        item = (
            loader.add_xpath("name", "//body/text()")
            .replace_xpath("name", "//div/text()")
            .add_css("description", "div::text")
            .replace_css("description", "p::text")
            .add_value("url", "http://example.com")
            .replace_value("url", "http://foo")
            .load_item()
        )
        self.assertEqual(
            item,
            {"name": ["marta"], "description": ["paragraph"], "url": ["http://foo"]},
        )
