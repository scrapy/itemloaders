import unittest

from parsel import Selector

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
        l = TestItemLoader()
        self.assertEqual(l.selector, None)

    def test_init_method_errors(self):
        l = TestItemLoader()
        self.assertRaises(RuntimeError, l.add_xpath, 'url', '//a/@href')
        self.assertRaises(RuntimeError, l.replace_xpath, 'url', '//a/@href')
        self.assertRaises(RuntimeError, l.get_xpath, '//a/@href')
        self.assertRaises(RuntimeError, l.add_css, 'name', '#name::text')
        self.assertRaises(RuntimeError, l.replace_css, 'name', '#name::text')
        self.assertRaises(RuntimeError, l.get_css, '#name::text')

    def test_init_method_with_selector(self):
        l = TestItemLoader(selector=self.selector)
        self.assertTrue(l.selector)

        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), ['Marta'])

    def test_init_method_with_selector_css(self):
        l = TestItemLoader(selector=self.selector)
        self.assertTrue(l.selector)

        l.add_css('name', 'div::text')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])

        l.add_css('url', 'a::attr(href)')
        self.assertEqual(l.get_output_value('url'), [u'http://www.scrapy.org'])

        # combining/accumulating CSS selectors and XPath expressions
        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), [u'Marta', u'Marta'])

        l.add_xpath('url', '//img/@src')
        self.assertEqual(l.get_output_value('url'), [u'http://www.scrapy.org', u'/images/logo.png'])

    def test_add_xpath_re(self):
        l = TestItemLoader(selector=self.selector)
        l.add_xpath('name', '//div/text()', re='ma')
        self.assertEqual(l.get_output_value('name'), ['Ma'])

    def test_replace_xpath(self):
        l = TestItemLoader(selector=self.selector)
        self.assertTrue(l.selector)
        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), ['Marta'])
        l.replace_xpath('name', '//p/text()')
        self.assertEqual(l.get_output_value('name'), ['Paragraph'])

        l.replace_xpath('name', ['//p/text()', '//div/text()'])
        self.assertEqual(l.get_output_value('name'), ['Paragraph', 'Marta'])

    def test_get_xpath(self):
        l = TestItemLoader(selector=self.selector)
        self.assertEqual(l.get_xpath('//p/text()'), ['paragraph'])
        self.assertEqual(l.get_xpath('//p/text()', TakeFirst()), 'paragraph')
        self.assertEqual(l.get_xpath('//p/text()', TakeFirst(), re='pa'), 'pa')

        self.assertEqual(l.get_xpath(['//p/text()', '//div/text()']), ['paragraph', 'marta'])

    def test_replace_xpath_multi_fields(self):
        l = TestItemLoader(selector=self.selector)
        l.add_xpath(None, '//div/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), ['Marta'])
        l.replace_xpath(None, '//p/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), ['Paragraph'])

    def test_replace_xpath_re(self):
        l = TestItemLoader(selector=self.selector)
        self.assertTrue(l.selector)
        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), ['Marta'])
        l.replace_xpath('name', '//div/text()', re='ma')
        self.assertEqual(l.get_output_value('name'), ['Ma'])

    def test_add_css_re(self):
        l = TestItemLoader(selector=self.selector)
        l.add_css('name', 'div::text', re='ma')
        self.assertEqual(l.get_output_value('name'), ['Ma'])

        l.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(l.get_output_value('url'), ['www.scrapy.org'])

    def test_replace_css(self):
        l = TestItemLoader(selector=self.selector)
        self.assertTrue(l.selector)
        l.add_css('name', 'div::text')
        self.assertEqual(l.get_output_value('name'), ['Marta'])
        l.replace_css('name', 'p::text')
        self.assertEqual(l.get_output_value('name'), ['Paragraph'])

        l.replace_css('name', ['p::text', 'div::text'])
        self.assertEqual(l.get_output_value('name'), ['Paragraph', 'Marta'])

        l.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(l.get_output_value('url'), ['www.scrapy.org'])
        l.replace_css('url', 'img::attr(src)')
        self.assertEqual(l.get_output_value('url'), ['/images/logo.png'])

    def test_get_css(self):
        l = TestItemLoader(selector=self.selector)
        self.assertEqual(l.get_css('p::text'), [u'paragraph'])
        self.assertEqual(l.get_css('p::text', TakeFirst()), 'paragraph')
        self.assertEqual(l.get_css('p::text', TakeFirst(), re='pa'), u'pa')

        self.assertEqual(l.get_css(['p::text', 'div::text']), ['paragraph', 'marta'])
        self.assertEqual(l.get_css(['a::attr(href)', 'img::attr(src)']),
                         [u'http://www.scrapy.org', '/images/logo.png'])

    def test_replace_css_multi_fields(self):
        l = TestItemLoader(selector=self.selector)
        l.add_css(None, 'div::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), ['Marta'])
        l.replace_css(None, 'p::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), ['Paragraph'])

        l.add_css(None, 'a::attr(href)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(l.get_output_value('url'), ['http://www.scrapy.org'])
        l.replace_css(None, 'img::attr(src)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(l.get_output_value('url'), ['/images/logo.png'])

    def test_replace_css_re(self):
        l = TestItemLoader(selector=self.selector)
        self.assertTrue(l.selector)
        l.add_css('url', 'a::attr(href)')
        self.assertEqual(l.get_output_value('url'), ['http://www.scrapy.org'])
        l.replace_css('url', 'a::attr(href)', re=r'http://www\.(.+)')
        self.assertEqual(l.get_output_value('url'), ['scrapy.org'])
