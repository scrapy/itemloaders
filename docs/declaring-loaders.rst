.. _declaring-loaders:

Declaring Item Loaders
======================

Item Loaders are declared by using a class definition syntax. Here is an example::

    from dataclasses import dataclass, field

    from itemloaders import ItemLoader
    from itemloaders.processors import TakeFirst


    def price_out(values):
        return float(values[0])


    @dataclass(init=False)
    class Product:
        name: str
        price: float = field(
            metadata={
            'output_processor': price_out
            }
        )


    class ProductLoader(ItemLoader):
        default_item_class = Product

        # using a built-in processor
        default_output_processor = TakeFirst()

        # using a function
        def name_in(self, values):
            return values[0].title()

    loader = ProductLoader()
    loader.add_value('name', 'plasma TV')
    loader.add_value('price', '999.98')
    # Product(name='Plasma Tv', price=999.98)

As you can see, input processors are declared using the ``_in`` suffix while
output processors are declared using the ``_out`` suffix. And you can also
declare a default input/output processors using the
:attr:`ItemLoader.default_input_processor` and
:attr:`ItemLoader.default_output_processor` attributes.

The precedence order, for both input and output processors, is as follows:

1. Item Loader field-specific attributes: ``field_in`` and ``field_out`` (most
   precedence)
2. Field metadata (``input_processor`` and ``output_processor`` key)
3. Item Loader defaults: :meth:`ItemLoader.default_input_processor` and
   :meth:`ItemLoader.default_output_processor` (least precedence)

See also: :ref:`extending-loaders`.
