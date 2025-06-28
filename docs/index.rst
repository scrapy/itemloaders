.. currentmodule:: itemloaders

.. _topics-index:

============
itemloaders
============

``itemloaders`` provide a convenient mechanism for populating data records.
Its design provides a flexible, efficient and easy mechanism
for extending and overriding different field parsing rules, either by raw data,
or by source format (HTML, XML, etc) without becoming a nightmare to maintain.

To install ``itemloaders``, run::

    pip install itemloaders

.. note:: Under the hood, ``itemloaders`` uses
    `itemadapter <https://github.com/scrapy/itemadapter>`_ as a common interface.
    This means you can use any of the types supported by ``itemadapter`` here.

.. warning:: ``dataclasses`` and ``attrs`` support is still experimental.
    Please, refer to :attr:`~ItemLoader.default_item_class` in the
    :ref:`api-reference` for more information.


Getting Started with ``itemloaders``
====================================

To use an Item Loader, you must first instantiate it. You can either
instantiate it with a dict-like object (`item`) or without one, in
which case an `item` is automatically instantiated in the Item Loader ``__init__`` method
using the `item` class specified in the :attr:`ItemLoader.default_item_class`
attribute.

Then, you start collecting values into the Item Loader, typically using
CSS or XPath Selectors. You can add more than one value to
the same item field; the Item Loader will know how to "join" those values later
using a proper processing function.

.. note:: Collected data is stored internally as lists,
   allowing to add several values to the same field.
   If an ``item`` argument is passed when creating a loader,
   each of the item's values will be stored as-is if it's already
   an iterable, or wrapped with a list if it's a single value.

Here is a typical Item Loader usage::

    from itemloaders import ItemLoader
    from parsel import Selector

    html_data = '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Some random product page</title>
        </head>
        <body>
            <div class="product_name">Some random product page</div>
            <p id="price">$ 100.12</p>
        </body>
    </html>
    '''
    l = ItemLoader(selector=Selector(html_data))
    l.add_xpath('name', '//div[@class="product_name"]/text()')
    l.add_xpath('name', '//div[@class="product_title"]/text()')
    l.add_css('price', '#price::text')
    l.add_value('last_updated', 'today') # you can also use literal values
    item = l.load_item()
    item
    # {'name': ['Some random product page'], 'price': ['$ 100.12'], 'last_updated': ['today']}

By quickly looking at that code, we can see the ``name`` field is being
extracted from two different XPath locations in the page:

1. ``//div[@class="product_name"]``
2. ``//div[@class="product_title"]``

In other words, data is being collected by extracting it from two XPath
locations, using the :meth:`~ItemLoader.add_xpath` method. This is the
data that will be assigned to the ``name`` field later.

Afterwards, similar calls are used for ``price`` field using a CSS selector with
the :meth:`~ItemLoader.add_css` method, and finally the ``last_update`` field is
populated directly with a literal value
(``today``) using a different method: :meth:`~ItemLoader.add_value`.

Finally, when all data is collected, the :meth:`ItemLoader.load_item` method is
called which actually returns the item populated with the data
previously extracted and collected with the :meth:`~ItemLoader.add_xpath`,
:meth:`~ItemLoader.add_css`, and :meth:`~ItemLoader.add_value` calls.

Contents
--------

.. toctree::
    declaring-loaders
    processors
    loaders-context
    nested-loaders
    extending-loaders
    built-in-processors
    api-reference
    release-notes
