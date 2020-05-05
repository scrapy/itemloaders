.. _loaders-context:

Item Loader Context
===================

The Item Loader Context is a mechanism that allows to change the input/ouput processors behavior.
It's just a ``dict`` of arbitrary key/values which is shared among all processors.
By default, the context contains the ``selector`` and any other `keyword arguments`
sent to the Loaders's ``__init__``.
The context can be passed when declaring, instantiating or using Item Loader.

For example, suppose you have a function ``parse_length`` which receives a text
value and extracts a length from it::

    def parse_length(text, loader_context):
        unit = loader_context.get('unit', 'm')
        # ... length parsing code goes here ...
        return parsed_length

By accepting a ``loader_context`` argument the function is explicitly telling
the Item Loader that it's able to receive an Item Loader context, so the Item
Loader passes the currently active context when calling it, and the processor
function (``parse_length`` in this case) can thus use them.

There are several ways to modify Item Loader context values:

1. By modifying the currently active Item Loader context
   (:attr:`~ItemLoader.context` attribute)::

      loader = ItemLoader(product)
      loader.context['unit'] = 'cm'

2. On Item Loader instantiation (the keyword arguments of Item Loader
   ``__init__`` method are stored in the Item Loader context)::

      loader = ItemLoader(product, unit='cm')

3. On Item Loader declaration, for those input/output processors that support
   instantiating them with an Item Loader context. :class:`~processor.MapCompose` is one of
   them::

       class ProductLoader(ItemLoader):
           length_out = MapCompose(parse_length, unit='cm')
