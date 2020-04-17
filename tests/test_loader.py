from functools import partial
import unittest

from itemloaders import ItemLoader, Item, Field, Selector
from itemloaders.processors import (Compose, Identity, Join,
                                      MapCompose, SelectJmes, TakeFirst)


# IGNORED FOR NOW


# test items
class NameItem(Item):
    name = Field()


class TestItem(NameItem):
    url = Field()
    summary = Field()


class TestNestedItem(Item):
    name = Field()
    name_div = Field()
    name_value = Field()

    url = Field()
    image = Field()


# test item loaders
class NameItemLoader(ItemLoader):
    default_item_class = TestItem


class NestedItemLoader(ItemLoader):
    default_item_class = TestNestedItem


class TestItemLoader(NameItemLoader):
    name_in = MapCompose(lambda v: v.title())


class DefaultedItemLoader(NameItemLoader):
    default_input_processor = MapCompose(lambda v: v[:-1])


# test processors
def processor_with_args(value, other=None, loader_context=None):
    if 'key' in loader_context:
        return loader_context['key']
    return value



class InitializationTestMixin:

    item_class = None

    def test_keep_single_value(self):
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo']})

    def test_keep_list(self):
        """Loaded item should contain values from the initial item"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar']})

    def test_add_value_singlevalue_singlevalue(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        il.add_value('name', 'bar')
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar']})

    def test_add_value_singlevalue_list(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        il.add_value('name', ['item', 'loader'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'item', 'loader']})

    def test_add_value_list_singlevalue(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        il.add_value('name', 'qwerty')
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar', 'qwerty']})

    def test_add_value_list_list(self):
        """Values added after initialization should be appended"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        il.add_value('name', ['item', 'loader'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(dict(loaded_item), {'name': ['foo', 'bar', 'item', 'loader']})

    def test_get_output_value_singlevalue(self):
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        self.assertEqual(il.get_output_value('name'), ['foo'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(loaded_item, dict({'name': ['foo']}))

    def test_get_output_value_list(self):
        """Getting output value must not remove value from item"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        self.assertEqual(il.get_output_value('name'), ['foo', 'bar'])
        loaded_item = il.load_item()
        self.assertIsInstance(loaded_item, self.item_class)
        self.assertEqual(loaded_item, dict({'name': ['foo', 'bar']}))

    def test_values_single(self):
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name='foo')
        il = ItemLoader(item=input_item)
        self.assertEqual(il._values.get('name'), ['foo'])

    def test_values_list(self):
        """Values from initial item must be added to loader._values"""
        input_item = self.item_class(name=['foo', 'bar'])
        il = ItemLoader(item=input_item)
        self.assertEqual(il._values.get('name'), ['foo', 'bar'])


class InitializationFromDictTest(InitializationTestMixin, unittest.TestCase):
    item_class = dict


class InitializationFromItemTest(InitializationTestMixin, unittest.TestCase):
    item_class = NameItem


class BaseNoInputReprocessingLoader(ItemLoader):
    title_in = MapCompose(str.upper)
    title_out = TakeFirst()


class NoInputReprocessingDictLoader(BaseNoInputReprocessingLoader):
    default_item_class = dict


class NoInputReprocessingFromDictTest(unittest.TestCase):
    """
    Loaders initialized from loaded items must not reprocess fields (dict instances)
    """
    def test_avoid_reprocessing_with_initial_values_single(self):
        il = NoInputReprocessingDictLoader(item=dict(title='foo'))
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, dict(title='foo'))
        self.assertEqual(NoInputReprocessingDictLoader(item=il_loaded).load_item(), dict(title='foo'))

    def test_avoid_reprocessing_with_initial_values_list(self):
        il = NoInputReprocessingDictLoader(item=dict(title=['foo', 'bar']))
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, dict(title='foo'))
        self.assertEqual(NoInputReprocessingDictLoader(item=il_loaded).load_item(), dict(title='foo'))

    def test_avoid_reprocessing_without_initial_values_single(self):
        il = NoInputReprocessingDictLoader()
        il.add_value('title', 'foo')
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, dict(title='FOO'))
        self.assertEqual(NoInputReprocessingDictLoader(item=il_loaded).load_item(), dict(title='FOO'))

    def test_avoid_reprocessing_without_initial_values_list(self):
        il = NoInputReprocessingDictLoader()
        il.add_value('title', ['foo', 'bar'])
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, dict(title='FOO'))
        self.assertEqual(NoInputReprocessingDictLoader(item=il_loaded).load_item(), dict(title='FOO'))


class NoInputReprocessingItem(Item):
    title = Field()


class NoInputReprocessingItemLoader(BaseNoInputReprocessingLoader):
    default_item_class = NoInputReprocessingItem


class NoInputReprocessingFromItemTest(unittest.TestCase):
    """
    Loaders initialized from loaded items must not reprocess fields (BaseItem instances)
    """
    def test_avoid_reprocessing_with_initial_values_single(self):
        il = NoInputReprocessingItemLoader(item=NoInputReprocessingItem(title='foo'))
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {'title': 'foo'})
        self.assertEqual(NoInputReprocessingItemLoader(item=il_loaded).load_item(), {'title': 'foo'})

    def test_avoid_reprocessing_with_initial_values_list(self):
        il = NoInputReprocessingItemLoader(item=NoInputReprocessingItem(title=['foo', 'bar']))
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {'title': 'foo'})
        self.assertEqual(NoInputReprocessingItemLoader(item=il_loaded).load_item(), {'title': 'foo'})

    def test_avoid_reprocessing_without_initial_values_single(self):
        il = NoInputReprocessingItemLoader()
        il.add_value('title', 'FOO')
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {'title': 'FOO'})
        self.assertEqual(NoInputReprocessingItemLoader(item=il_loaded).load_item(), {'title': 'FOO'})

    def test_avoid_reprocessing_without_initial_values_list(self):
        il = NoInputReprocessingItemLoader()
        il.add_value('title', ['foo', 'bar'])
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {'title': 'FOO'})
        self.assertEqual(NoInputReprocessingItemLoader(item=il_loaded).load_item(), {'title': 'FOO'})


class TestOutputProcessorDict(unittest.TestCase):
    def test_output_processor(self):

        class TempDict(dict):
            def __init__(self, *args, **kwargs):
                super(TempDict, self).__init__(self, *args, **kwargs)
                self.setdefault('temp', 0.3)

        class TempLoader(ItemLoader):
            default_item_class = TempDict
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        loader = TempLoader()
        item = loader.load_item()
        self.assertIsInstance(item, TempDict)
        self.assertEqual(dict(item), {'temp': 0.3})


class TestOutputProcessorItem(unittest.TestCase):
    def test_output_processor(self):

        class TempItem(Item):
            temp = Field()

            def __init__(self, *args, **kwargs):
                super(TempItem, self).__init__(self, *args, **kwargs)
                self.setdefault('temp', 0.3)

        class TempLoader(ItemLoader):
            default_item_class = TempItem
            default_input_processor = Identity()
            default_output_processor = Compose(TakeFirst())

        loader = TempLoader()
        item = loader.load_item()
        self.assertIsInstance(item, TempItem)
        self.assertEqual(dict(item), {'temp': 0.3})


class ProcessorsTest(unittest.TestCase):

    def test_take_first(self):
        proc = TakeFirst()
        self.assertEqual(proc([None, '', 'hello', 'world']), 'hello')
        self.assertEqual(proc([None, '', 0, 'hello', 'world']), 0)

    def test_identity(self):
        proc = Identity()
        self.assertEqual(proc([None, '', 'hello', 'world']),
                         [None, '', 'hello', 'world'])

    def test_join(self):
        proc = Join()
        self.assertRaises(TypeError, proc, [None, '', 'hello', 'world'])
        self.assertEqual(proc(['', 'hello', 'world']), u' hello world')
        self.assertEqual(proc(['hello', 'world']), u'hello world')
        self.assertIsInstance(proc(['hello', 'world']), str)

    def test_compose(self):
        proc = Compose(lambda v: v[0], str.upper)
        self.assertEqual(proc(['hello', 'world']), 'HELLO')
        proc = Compose(str.upper)
        self.assertEqual(proc(None), None)
        proc = Compose(str.upper, stop_on_none=False)
        self.assertRaises(ValueError, proc, None)
        proc = Compose(str.upper, lambda x: x + 1)
        self.assertRaises(ValueError, proc, 'hello')

    def test_mapcompose(self):
        def filter_world(x):
            return None if x == 'world' else x
        proc = MapCompose(filter_world, str.upper)
        self.assertEqual(proc([u'hello', u'world', u'this', u'is', u'scrapy']),
                         [u'HELLO', u'THIS', u'IS', u'SCRAPY'])
        proc = MapCompose(filter_world, str.upper)
        self.assertEqual(proc(None), [])
        proc = MapCompose(filter_world, str.upper)
        self.assertRaises(ValueError, proc, [1])
        proc = MapCompose(filter_world, lambda x: x + 1)
        self.assertRaises(ValueError, proc, 'hello')


class SelectortemLoaderTest(unittest.TestCase):
    response = HtmlResponse(url="", encoding='utf-8', body=b"""
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
        sel = Selector(text=u"<html><body><div>marta</div></body></html>")
        l = TestItemLoader(selector=sel)
        self.assertIs(l.selector, sel)

        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])

    def test_init_method_with_selector_css(self):
        sel = Selector(text=u"<html><body><div>marta</div></body></html>")
        l = TestItemLoader(selector=sel)
        self.assertIs(l.selector, sel)

        l.add_css('name', 'div::text')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])

    def test_init_method_with_response(self):
        l = TestItemLoader(response=self.response)
        self.assertTrue(l.selector)

        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])

    def test_init_method_with_response_css(self):
        l = TestItemLoader(response=self.response)
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
        l = TestItemLoader(response=self.response)
        l.add_xpath('name', '//div/text()', re='ma')
        self.assertEqual(l.get_output_value('name'), [u'Ma'])

    def test_replace_xpath(self):
        l = TestItemLoader(response=self.response)
        self.assertTrue(l.selector)
        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])
        l.replace_xpath('name', '//p/text()')
        self.assertEqual(l.get_output_value('name'), [u'Paragraph'])

        l.replace_xpath('name', ['//p/text()', '//div/text()'])
        self.assertEqual(l.get_output_value('name'), [u'Paragraph', 'Marta'])

    def test_get_xpath(self):
        l = TestItemLoader(response=self.response)
        self.assertEqual(l.get_xpath('//p/text()'), [u'paragraph'])
        self.assertEqual(l.get_xpath('//p/text()', TakeFirst()), u'paragraph')
        self.assertEqual(l.get_xpath('//p/text()', TakeFirst(), re='pa'), u'pa')

        self.assertEqual(l.get_xpath(['//p/text()', '//div/text()']), [u'paragraph', 'marta'])

    def test_replace_xpath_multi_fields(self):
        l = TestItemLoader(response=self.response)
        l.add_xpath(None, '//div/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), [u'Marta'])
        l.replace_xpath(None, '//p/text()', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), [u'Paragraph'])

    def test_replace_xpath_re(self):
        l = TestItemLoader(response=self.response)
        self.assertTrue(l.selector)
        l.add_xpath('name', '//div/text()')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])
        l.replace_xpath('name', '//div/text()', re='ma')
        self.assertEqual(l.get_output_value('name'), [u'Ma'])

    def test_add_css_re(self):
        l = TestItemLoader(response=self.response)
        l.add_css('name', 'div::text', re='ma')
        self.assertEqual(l.get_output_value('name'), [u'Ma'])

        l.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(l.get_output_value('url'), [u'www.scrapy.org'])

    def test_replace_css(self):
        l = TestItemLoader(response=self.response)
        self.assertTrue(l.selector)
        l.add_css('name', 'div::text')
        self.assertEqual(l.get_output_value('name'), [u'Marta'])
        l.replace_css('name', 'p::text')
        self.assertEqual(l.get_output_value('name'), [u'Paragraph'])

        l.replace_css('name', ['p::text', 'div::text'])
        self.assertEqual(l.get_output_value('name'), [u'Paragraph', 'Marta'])

        l.add_css('url', 'a::attr(href)', re='http://(.+)')
        self.assertEqual(l.get_output_value('url'), [u'www.scrapy.org'])
        l.replace_css('url', 'img::attr(src)')
        self.assertEqual(l.get_output_value('url'), [u'/images/logo.png'])

    def test_get_css(self):
        l = TestItemLoader(response=self.response)
        self.assertEqual(l.get_css('p::text'), [u'paragraph'])
        self.assertEqual(l.get_css('p::text', TakeFirst()), u'paragraph')
        self.assertEqual(l.get_css('p::text', TakeFirst(), re='pa'), u'pa')

        self.assertEqual(l.get_css(['p::text', 'div::text']), [u'paragraph', 'marta'])
        self.assertEqual(l.get_css(['a::attr(href)', 'img::attr(src)']),
                         [u'http://www.scrapy.org', u'/images/logo.png'])

    def test_replace_css_multi_fields(self):
        l = TestItemLoader(response=self.response)
        l.add_css(None, 'div::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), [u'Marta'])
        l.replace_css(None, 'p::text', TakeFirst(), lambda x: {'name': x})
        self.assertEqual(l.get_output_value('name'), [u'Paragraph'])

        l.add_css(None, 'a::attr(href)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(l.get_output_value('url'), [u'http://www.scrapy.org'])
        l.replace_css(None, 'img::attr(src)', TakeFirst(), lambda x: {'url': x})
        self.assertEqual(l.get_output_value('url'), [u'/images/logo.png'])

    def test_replace_css_re(self):
        l = TestItemLoader(response=self.response)
        self.assertTrue(l.selector)
        l.add_css('url', 'a::attr(href)')
        self.assertEqual(l.get_output_value('url'), [u'http://www.scrapy.org'])
        l.replace_css('url', 'a::attr(href)', re=r'http://www\.(.+)')
        self.assertEqual(l.get_output_value('url'), [u'scrapy.org'])


class SubselectorLoaderTest(unittest.TestCase):
    response = HtmlResponse(url="", encoding='utf-8', body=b"""
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
    """)

    def test_nested_xpath(self):
        l = NestedItemLoader(response=self.response)
        nl = l.nested_xpath("//header")
        nl.add_xpath('name', 'div/text()')
        nl.add_css('name_div', '#id')
        nl.add_value('name_value', nl.selector.xpath('div[@id = "id"]/text()').getall())

        self.assertEqual(l.get_output_value('name'), [u'marta'])
        self.assertEqual(l.get_output_value('name_div'), [u'<div id="id">marta</div>'])
        self.assertEqual(l.get_output_value('name_value'), [u'marta'])

        self.assertEqual(l.get_output_value('name'), nl.get_output_value('name'))
        self.assertEqual(l.get_output_value('name_div'), nl.get_output_value('name_div'))
        self.assertEqual(l.get_output_value('name_value'), nl.get_output_value('name_value'))

    def test_nested_css(self):
        l = NestedItemLoader(response=self.response)
        nl = l.nested_css("header")
        nl.add_xpath('name', 'div/text()')
        nl.add_css('name_div', '#id')
        nl.add_value('name_value', nl.selector.xpath('div[@id = "id"]/text()').getall())

        self.assertEqual(l.get_output_value('name'), [u'marta'])
        self.assertEqual(l.get_output_value('name_div'), [u'<div id="id">marta</div>'])
        self.assertEqual(l.get_output_value('name_value'), [u'marta'])

        self.assertEqual(l.get_output_value('name'), nl.get_output_value('name'))
        self.assertEqual(l.get_output_value('name_div'), nl.get_output_value('name_div'))
        self.assertEqual(l.get_output_value('name_value'), nl.get_output_value('name_value'))

    def test_nested_replace(self):
        l = NestedItemLoader(response=self.response)
        nl1 = l.nested_xpath('//footer')
        nl2 = nl1.nested_xpath('a')

        l.add_xpath('url', '//footer/a/@href')
        self.assertEqual(l.get_output_value('url'), [u'http://www.scrapy.org'])
        nl1.replace_xpath('url', 'img/@src')
        self.assertEqual(l.get_output_value('url'), [u'/images/logo.png'])
        nl2.replace_xpath('url', '@href')
        self.assertEqual(l.get_output_value('url'), [u'http://www.scrapy.org'])

    def test_nested_ordering(self):
        l = NestedItemLoader(response=self.response)
        nl1 = l.nested_xpath('//footer')
        nl2 = nl1.nested_xpath('a')

        nl1.add_xpath('url', 'img/@src')
        l.add_xpath('url', '//footer/a/@href')
        nl2.add_xpath('url', 'text()')
        l.add_xpath('url', '//footer/a/@href')

        self.assertEqual(l.get_output_value('url'), [
            u'/images/logo.png',
            u'http://www.scrapy.org',
            u'homepage',
            u'http://www.scrapy.org',
        ])

    def test_nested_load_item(self):
        l = NestedItemLoader(response=self.response)
        nl1 = l.nested_xpath('//footer')
        nl2 = nl1.nested_xpath('img')

        l.add_xpath('name', '//header/div/text()')
        nl1.add_xpath('url', 'a/@href')
        nl2.add_xpath('image', '@src')

        item = l.load_item()

        assert item is l.item
        assert item is nl1.item
        assert item is nl2.item

        self.assertEqual(item['name'], [u'marta'])
        self.assertEqual(item['url'], [u'http://www.scrapy.org'])
        self.assertEqual(item['image'], [u'/images/logo.png'])


class SelectJmesTestCase(unittest.TestCase):
    test_list_equals = {
        'simple': ('foo.bar', {"foo": {"bar": "baz"}}, "baz"),
        'invalid': ('foo.bar.baz', {"foo": {"bar": "baz"}}, None),
        'top_level': ('foo', {"foo": {"bar": "baz"}}, {"bar": "baz"}),
        'double_vs_single_quote_string': ('foo.bar', {"foo": {"bar": "baz"}}, "baz"),
        'dict': (
            'foo.bar[*].name',
            {"foo": {"bar": [{"name": "one"}, {"name": "two"}]}},
            ['one', 'two']
        ),
        'list': ('[1]', [1, 2], 2)
    }

    def test_output(self):
        for l in self.test_list_equals:
            expr, test_list, expected = self.test_list_equals[l]
            test = SelectJmes(expr)(test_list)
            self.assertEqual(
                test,
                expected,
                msg='test "{}" got {} expected {}'.format(l, test, expected)
            )


# Functions as processors

def function_processor_strip(iterable):
    return [x.strip() for x in iterable]


def function_processor_upper(iterable):
    return [x.upper() for x in iterable]


class FunctionProcessorItem(Item):
    foo = Field(
        input_processor=function_processor_strip,
        output_processor=function_processor_upper,
    )


class FunctionProcessorItemLoader(ItemLoader):
    default_item_class = FunctionProcessorItem


class FunctionProcessorDictLoader(ItemLoader):
    default_item_class = dict
    foo_in = function_processor_strip
    foo_out = function_processor_upper


class FunctionProcessorTestCase(unittest.TestCase):

    def test_processor_defined_in_item(self):
        lo = FunctionProcessorItemLoader()
        lo.add_value('foo', '  bar  ')
        lo.add_value('foo', ['  asdf  ', '  qwerty  '])
        self.assertEqual(
            dict(lo.load_item()),
            {'foo': ['BAR', 'ASDF', 'QWERTY']}
        )

    def test_processor_defined_in_item_loader(self):
        lo = FunctionProcessorDictLoader()
        lo.add_value('foo', '  bar  ')
        lo.add_value('foo', ['  asdf  ', '  qwerty  '])
        self.assertEqual(
            dict(lo.load_item()),
            {'foo': ['BAR', 'ASDF', 'QWERTY']}
        )


if __name__ == "__main__":
    unittest.main()
