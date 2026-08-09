.. _extending-loaders:

Reusing and extending Item Loaders
==================================

Item Loaders are designed to ease the maintenance burden of parsing rules,
without losing flexibility and, at the same time, providing a convenient
mechanism for extending and overriding them. For this reason Item Loaders
support traditional Python class inheritance for dealing with differences
in data schemas.

Suppose, for example, that you get some particular product names enclosed in
three dashes (e.g. ``---Plasma TV---``) and you don't want to end up with
those dashes in the final product names.

Here's how you can remove those dashes by reusing and extending the default
Product Item Loader (``ProductLoader``)::

    from itemloaders.processors import MapCompose
    from myproject.loaders import ProductLoader

    def strip_dashes(x):
        return x.strip('-')

    class SiteSpecificLoader(ProductLoader):
        name_in = MapCompose(strip_dashes, ProductLoader.name_in)

Another case where extending Item Loaders can be very helpful is when you have
multiple source formats, for example XML and HTML. In the XML version you may
want to remove ``CDATA`` occurrences. Here's an example of how to do it::

    from itemloaders.processors import MapCompose
    from myproject.ItemLoaders import ProductLoader
    from myproject.utils.xml import remove_cdata

    class XmlProductLoader(ProductLoader):
        name_in = MapCompose(remove_cdata, ProductLoader.name_in)

And that's how you typically extend input/output processors.

There are many other possible ways to extend, inherit and override your Item
Loaders, and different Item Loaders hierarchies may fit better for different
projects. ``itemloaders`` only provides the mechanism; it doesn't impose any specific
organization of your Loaders collection - that's up to you and your project's
needs.

Tracking parser rule usage
--------------------------

When a field has fallback rules for layouts that a site only serves sometimes,
it is hard to tell which of those rules are still worth keeping. Override
:meth:`~itemloaders.ItemLoader.add_css` to count how often each rule matches::

    from collections import defaultdict

    from itemloaders import ItemLoader
    from itemloaders.utils import arg_to_iter

    class TrackingLoader(ItemLoader):
        def __init__(self, *args, stats=None, **kwargs):
            super().__init__(*args, **kwargs)
            self.stats = stats
            self._positions = defaultdict(int)

        def add_css(self, field_name, css, *processors, **kwargs):
            values = []
            for rule in arg_to_iter(css):
                self._positions[field_name] += 1
                key = f"parser/{field_name}/css/{self._positions[field_name]}"
                matches = self.selector.css(rule).getall()
                self.stats.inc_value(key if matches else f"{key}/missing")
                values.extend(matches)
            return self.add_value(field_name, values, *processors, **kwargs)

*stats* is any object with an ``inc_value`` method, such as the stats collector
of a Scrapy crawler, which you would pass as
``TrackingLoader(response=response, stats=self.crawler.stats)``. After a crawl
where the second rule below never matched, its counters read
``parser/name/css/1: 87`` and ``parser/name/css/2/missing: 87``::

    loader.add_css('name', ['h1::text', 'meta[name="title"]::attr(content)'])

A rule whose only counter is the ``/missing`` one is safe to remove.
