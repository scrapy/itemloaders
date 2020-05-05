.. _declaring-loaders:

Declaring Item Loaders
======================

Item Loaders are declared by using a class definition syntax. Here is an example::

    from itemloaders import ItemLoader
    from itemloaders.processors import TakeFirst, MapCompose, Join

    class ProductLoader(ItemLoader):

        default_output_processor = TakeFirst()

        name_in = MapCompose(str.title)
        name_out = Join()

        # using a built-in processor
        price_in = MapCompose(str.strip)

        # using a function
        def price_out(self, values):
            return float(values[0])

As you can see, input processors are declared using the ``_in`` suffix while
output processors are declared using the ``_out`` suffix. And you can also
declare a default input/output processors using the
:attr:`ItemLoader.default_input_processor` and
:attr:`ItemLoader.default_output_processor` attributes.

The precedence order, for both input and output processors, is as follows:

1. Item Loader field-specific attributes: ``field_in`` and ``field_out`` (most
   precedence)
2. Item Loader defaults: :meth:`ItemLoader.default_input_processor` and
   :meth:`ItemLoader.default_output_processor` (least precedence)

See also: :ref:`extending-loaders`.
