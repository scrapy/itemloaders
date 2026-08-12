.. _rule-usage:

Tracking parsing rule usage
===========================

.. versionadded:: VERSION

When a field has fallback rules for layouts that a website only serves
sometimes, it is hard to tell which of those rules are still worth keeping.
Pass a *stats* object, i.e. any object with an ``inc_value(key, count)``
method, such as the :ref:`stats collector <topics-stats>` of a Scrapy crawler,
and every parsing rule gets a counter of the number of times that it matched
something::

    loader = ItemLoader(selector=selector, stats=stats)
    loader.add_css('name', ['h1::text', 'meta[name="title"]::attr(content)'])

After a crawl where the second rule above never matched, the counters read:

.. code-block:: none

    parser/name/css/h1::text: 87
    parser/name/css/meta[name="title"]::attr(content): 0

A rule at 0 is safe to remove. A rule above 0 did match, which does not
necessarily mean that its data reached the item; an output processor such as
:class:`~itemloaders.processors.TakeFirst` may still have discarded it in favor
of the data of an earlier rule.

Rules used without a field name, e.g. through
:meth:`~itemloaders.ItemLoader.get_css`, are counted under ``<none>``, as in
``parser/<none>/css/h1::text``.
