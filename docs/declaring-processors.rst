.. _declaring-processors:

Declaring Input and Output Processors
=====================================

As seen in the previous section, input and output processors can be declared in
the Item Loader definition, and it's very common to declare input processors
this way. However, there is one more place where you can specify the input and
output processors to use: in the :ref:`Item Field <topics-items-fields>`
metadata. Here is an example::

    import scrapy
    from scrapy.loader.processors import Join, MapCompose, TakeFirst
    from w3lib.html import remove_tags

    def filter_price(value):
        if value.isdigit():
            return value

    class Product(scrapy.Item):
        name = scrapy.Field(
            input_processor=MapCompose(remove_tags),
            output_processor=Join(),
        )
        price = scrapy.Field(
            input_processor=MapCompose(remove_tags, filter_price),
            output_processor=TakeFirst(),
        )

>>> from scrapy.loader import ItemLoader
>>> il = ItemLoader(item=Product())
>>> il.add_value('name', [u'Welcome to my', u'<strong>website</strong>'])
>>> il.add_value('price', [u'&euro;', u'<span>1000</span>'])
>>> il.load_item()
{'name': u'Welcome to my website', 'price': u'1000'}

The precedence order, for both input and output processors, is as follows:

1. Item Loader field-specific attributes: ``field_in`` and ``field_out`` (most
   precedence)
2. Field metadata (``input_processor`` and ``output_processor`` key)
3. Item Loader defaults: :meth:`ItemLoader.default_input_processor` and
   :meth:`ItemLoader.default_output_processor` (least precedence)

See also: :ref:`topics-loaders-extending`.