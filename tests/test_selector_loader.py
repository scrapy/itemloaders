import unittest
import pytest
from unittest import mock

from parsel import Selector
from parsel.utils import flatten

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


class TestItemLoader(ItemLoader):
    name_in = MapCompose(lambda v: v.title())


class SelectortemLoaderTest(unittest.TestCase):
    selector = Selector(text="""
    <html>
    <body>
    <div id="id">marta</div>
    <p>paragraph</p>
    <a href="http://www.scrapy.org">homepage</a>
    <img src="/images/logo.png" width="244" height="65" alt="Scrapy">
    </body>
    </html>
    """)

    def test_init_method(self):
        loader = TestItemLoader()
        self.assertEqual(loader.selector, None)

    def test_init_method_errors(self):
        loader = TestItemLoader()
        self.assertRaises(RuntimeError, loader.add_xpath, 'url', '//a/@href')
        self.assertRaises(RuntimeError, loader.replace_xpath, 'url', '//a/@href')
        self.assertRaises(RuntimeError, loader.get_xpath, '//a/@href')
        self.assertRaises(RuntimeError, loader.add_css, 'name', '#name::text')
        self.assertRaises(RuntimeError, loader.replace_css, 'name', '#name::text')
        self.assertRaises(RuntimeError, loader.get_css, '#name::text')

    def test_init_method_with_selector(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)

        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])

    def test_init_method_with_selector_css(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)

        loader.add_css('name', 'div::text')
        self.assertEqual(loader.get_output_value('name'), [u'Marta'])

        loader.add_css('url', 'a::attr(href)')
        self.assertEqual(loader.get_output_value('url'), [u'http://www.scrapy.org'])

        # combining/accumulating CSS selectors and XPath expressions
        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), [u'Marta', u'Marta'])

        loader.add_xpath('url', '//img/@src')
        self.assertEqual(loader.get_output_value('url'), [u'http://www.scrapy.org', u'/images/logo.png'])

    def test_add_xpath_re(self):
        loader = TestItemLoader(selector=self.selector)
        loader.add_xpath('name', '//div/text()', re='ma')
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

    def test_replace_xpath(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_xpath('name', '//p/text()')
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

        loader.replace_xpath('name', ['//p/text()', '//div/text()'])
        self.assertEqual(loader.get_output_value('name'), ['Paragraph', 'Marta'])

    def test_get_xpath(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertEqual(loader.get_xpath('//p/text()'), ['paragraph'])
        self.assertEqual(loader.get_xpath('//p/text()', TakeFirst()), 'paragraph')
        self.assertEqual(loader.get_xpath('//p/text()', TakeFirst(), re='pa'), 'pa')

        self.assertEqual(loader.get_xpath(['//p/text()', '//div/text()']), ['paragraph', 'marta'])

    def test_replace_xpath_multi_fields(self):
        loader = TestItemLoader(selector=self.selector)
        loader.add_xpath(None, '//div/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_xpath(None, '//p/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

    def test_replace_xpath_re(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_xpath('name', '//div/text()', re='ma')
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

    def test_add_css_re(self):
        loader = TestItemLoader(selector=self.selector)
        loader.add_css('name', 'div::text', re='ma')
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

        loader.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(loader.get_output_value('url'), ['www.scrapy.org'])

    def test_replace_css(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_css('name', 'div::text')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_css('name', 'p::text')
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

        loader.replace_css('name', ['p::text', 'div::text'])
        self.assertEqual(loader.get_output_value('name'), ['Paragraph', 'Marta'])

        loader.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(loader.get_output_value('url'), ['www.scrapy.org'])
        loader.replace_css('url', 'img::attr(src)')
        self.assertEqual(loader.get_output_value('url'), ['/images/logo.png'])

    def test_get_css(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertEqual(loader.get_css('p::text'), [u'paragraph'])
        self.assertEqual(loader.get_css('p::text', TakeFirst()), 'paragraph')
        self.assertEqual(loader.get_css('p::text', TakeFirst(), re='pa'), u'pa')

        self.assertEqual(loader.get_css(['p::text', 'div::text']), ['paragraph', 'marta'])
        self.assertEqual(loader.get_css(['a::attr(href)', 'img::attr(src)']),
                         [u'http://www.scrapy.org', '/images/logo.png'])

    def test_replace_css_multi_fields(self):
        loader = TestItemLoader(selector=self.selector)
        loader.add_css(None, 'div::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_css(None, 'p::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

        loader.add_css(None, 'a::attr(href)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(loader.get_output_value('url'), ['http://www.scrapy.org'])
        loader.replace_css(None, 'img::attr(src)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(loader.get_output_value('url'), ['/images/logo.png'])

    def test_replace_css_re(self):
        loader = TestItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_css('url', 'a::attr(href)')
        self.assertEqual(loader.get_output_value('url'), ['http://www.scrapy.org'])
        loader.replace_css('url', 'a::attr(href)', re=r'http://www\.(.+)')
        self.assertEqual(loader.get_output_value('url'), ['scrapy.org'])


def test_get_selector_values_with_no_selector():
    """It should raise an error if it's not configured with any Selector."""

    loader = ItemLoader()

    with pytest.raises(RuntimeError) as err:
        loader.get_selector_values("field_name", [], None)


def test_get_selector_values():
    """Selectors must be properly called as well as correctly flatten the data.

    For this test, we're testing 'css', but it should also work the same for 'xpath'.
    """

    selector_rules = ["#rule1", "#rule2", "#rule3"]
    field_name = "field"
    parsed_data = ["data1", "data2"]

    mock_css_selector = mock.Mock()
    mock_css_selector().getall.return_value = parsed_data
    mock_css_selector.__name__ = "css"

    mock_selector = mock.Mock()
    mock_selector.css = mock_css_selector

    loader = ItemLoader(selector=mock_selector)
    loader.write_to_stats = mock.Mock()

    # This wasn't actually initialized so it will return 0 by default otherwise.
    loader.field_tracker["field_css"] = 1

    result = loader.get_selector_values(field_name, selector_rules, "css")

    assert result == flatten([parsed_data] * len(selector_rules))

    mock_selector.assert_has_calls(
        [
            mock.call.css(selector_rules[0]),
            mock.call.css().getall(),
            mock.call.css(selector_rules[1]),
            mock.call.css().getall(),
            mock.call.css(selector_rules[2]),
            mock.call.css().getall(),
        ]
    )

    loader.write_to_stats.assert_has_calls(
        [
            mock.call(field_name, parsed_data, 1, "css", name=None),
            mock.call(field_name, parsed_data, 2, "css", name=None),
            mock.call(field_name, parsed_data, 3, "css", name=None),
        ]
    )
