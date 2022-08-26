import re
import unittest

from parsel import Selector

from itemloaders import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


class CustomItemLoader(ItemLoader):
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
        loader = CustomItemLoader()
        self.assertEqual(loader.selector, None)

    def test_init_method_errors(self):
        loader = CustomItemLoader()
        self.assertRaises(RuntimeError, loader.add_xpath, 'url', '//a/@href')
        self.assertRaises(RuntimeError, loader.replace_xpath, 'url', '//a/@href')
        self.assertRaises(RuntimeError, loader.get_xpath, '//a/@href')
        self.assertRaises(RuntimeError, loader.add_css, 'name', '#name::text')
        self.assertRaises(RuntimeError, loader.replace_css, 'name', '#name::text')
        self.assertRaises(RuntimeError, loader.get_css, '#name::text')

    def test_init_method_with_selector(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)

        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])

    def test_init_method_with_selector_css(self):
        loader = CustomItemLoader(selector=self.selector)
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
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath('name', '//div/text()', re='ma')
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath('name', '//div/text()', re=re.compile('ma'))
        self.assertEqual(loader.get_output_value('name'), ['Ma'])


    def test_add_xpath_variables(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath('name', 'id($id)/text()', id="id")
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath('name', 'id($id)/text()', id="id2")
        self.assertEqual(loader.get_output_value('name'), [])

    def test_replace_xpath(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_xpath('name', '//p/text()')
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

        loader.replace_xpath('name', ['//p/text()', '//div/text()'])
        self.assertEqual(loader.get_output_value('name'), ['Paragraph', 'Marta'])

    def test_get_xpath(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertEqual(loader.get_xpath('//p/text()'), ['paragraph'])
        self.assertEqual(loader.get_xpath('//p/text()', TakeFirst()), 'paragraph')
        self.assertEqual(loader.get_xpath('//p/text()', TakeFirst(), re='pa'), 'pa')

        self.assertEqual(loader.get_xpath(['//p/text()', '//div/text()']), ['paragraph', 'marta'])

    def test_replace_xpath_multi_fields(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_xpath(None, '//div/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_xpath(None, '//p/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

    def test_replace_xpath_re(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_xpath('name', '//div/text()')
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_xpath('name', '//div/text()', re='ma')
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

    def test_add_css_re(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_css('name', 'div::text', re='ma')
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

        loader.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(loader.get_output_value('url'), ['www.scrapy.org'])

        loader = CustomItemLoader(selector=self.selector)
        loader.add_css('name', 'div::text', re=re.compile('ma'))
        self.assertEqual(loader.get_output_value('name'), ['Ma'])

        loader.add_css('url', 'a::attr(href)', re=re.compile('http://(.+)'))
        self.assertEqual(loader.get_output_value('url'), ['www.scrapy.org'])

    def test_replace_css(self):
        loader = CustomItemLoader(selector=self.selector)
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
        loader = CustomItemLoader(selector=self.selector)
        self.assertEqual(loader.get_css('p::text'), [u'paragraph'])
        self.assertEqual(loader.get_css('p::text', TakeFirst()), 'paragraph')
        self.assertEqual(loader.get_css('p::text', TakeFirst(), re='pa'), u'pa')

        self.assertEqual(loader.get_css(['p::text', 'div::text']), ['paragraph', 'marta'])
        self.assertEqual(loader.get_css(['a::attr(href)', 'img::attr(src)']),
                         [u'http://www.scrapy.org', '/images/logo.png'])

    def test_replace_css_multi_fields(self):
        loader = CustomItemLoader(selector=self.selector)
        loader.add_css(None, 'div::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Marta'])
        loader.replace_css(None, 'p::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(loader.get_output_value('name'), ['Paragraph'])

        loader.add_css(None, 'a::attr(href)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(loader.get_output_value('url'), ['http://www.scrapy.org'])
        loader.replace_css(None, 'img::attr(src)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(loader.get_output_value('url'), ['/images/logo.png'])

    def test_replace_css_re(self):
        loader = CustomItemLoader(selector=self.selector)
        self.assertTrue(loader.selector)
        loader.add_css('url', 'a::attr(href)')
        self.assertEqual(loader.get_output_value('url'), ['http://www.scrapy.org'])
        loader.replace_css('url', 'a::attr(href)', re=r'http://www\.(.+)')
        self.assertEqual(loader.get_output_value('url'), ['scrapy.org'])
