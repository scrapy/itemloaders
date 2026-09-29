.. currentmodule:: itemloaders

.. _release-notes:

Release notes
=============

.. _release-1.5.0:

itemloaders 1.5.0 (unreleased)
------------------------------

-   **Backward-incompatible change:** when an Item Loader instantiates the
    item itself, from :attr:`~ItemLoader.default_item_class`, the field
    defaults of that item are no longer treated as collected data, so they no
    longer go through processors and no longer get combined with the values
    you add. They still reach the loaded item for fields that get no data.

    To get the old behavior, pass the item yourself, e.g.
    ``ItemLoader(item=MyItem())``. (:gh:`117`)

-   **Backward-incompatible change:** sets and iterators other than generators,
    such as the result of :func:`map`, are now collected value by value, like
    lists, tuples and generators already were, instead of as a single value.

    To collect one of them as a single value, wrap it in a list, e.g.
    ``loader.add_value("tags", [{"a", "b"}])``. (:gh:`120`)

-   Added a *stats* parameter to :class:`ItemLoader` to count how often each
    parsing rule matches, to find rules that are no longer needed. See
    :ref:`rule-usage`. (:gh:`121`)

-   :ref:`Nested loaders <nested-loaders>` now inherit the
    :ref:`context <loaders-context>` of their parent loader, with keyword
    arguments passed to :meth:`~ItemLoader.nested_xpath` and
    :meth:`~ItemLoader.nested_css` taking precedence. (:gh:`34`, :gh:`124`)

-   Fixed :func:`functools.partial` processors missing their
    ``loader_context`` when the value of a positionally-bound argument matched
    the name of an unbound parameter, e.g. ``partial(func, "loader_context")``.
    (:gh:`125`, :gh:`126`)

-   Improved performance. (:gh:`119`, :gh:`120`)

-   Documentation improvements. (:gh:`111`, :gh:`116`, :gh:`118`)

-   CI and test improvements. (:gh:`114`, :gh:`115`, :gh:`122`, :gh:`123`,
    :gh:`127`)

.. _release-1.4.0:

itemloaders 1.4.0 (2026-01-29)
------------------------------

-   Dropped support for Python 3.8-3.9 and PyPy 3.9-3.10 (:gh:`94`, :gh:`104`)

-   Added support for Python 3.14 and PyPy 3.11 (:gh:`98`, :gh:`104`)

-   Switched the build system to ``hatchling`` (:gh:`100`)

-   Documentation improvements (:gh:`106`)

-   CI improvements (:gh:`95`, :gh:`96`, :gh:`97`, :gh:`99`, :gh:`102`,
    :gh:`103`, :gh:`107`)

.. _release-1.3.2:

itemloaders 1.3.2 (2024-09-30)
------------------------------

-   Added official support for the upcoming Python 3.13 (:gh:`91`)

-   Removed ``w3lib`` from direct dependencies (it's not used directly but is
    an indirect dependency via ``parsel``). (:gh:`90`)

-   Improved CI (:gh:`92`)

.. _release-1.3.1:

itemloaders 1.3.1 (2024-06-03)
------------------------------

-   Fixed an error when using nested loaders with empty matches that was
    introduced in 1.3.0 (:gh:`88`)

.. _release-1.3.0:

itemloaders 1.3.0 (2024-05-30)
------------------------------

-   Added support for method chaining to the ``add_*`` and ``replace_*``
    methods, so you can now write code such as
    ``loader.add_xpath("name", "//body/text()").add_value("url", "http://example.com")``
    (:gh:`81`)

-   Added type hints and ``py.typed`` (:gh:`80`, :gh:`83`)

-   Made the docs builds reproducible (:gh:`82`)

.. _release-1.2.0:

itemloaders 1.2.0 (2024-04-18)
------------------------------

-   Added official support for Python 3.12 and PyPy 3.10 (:gh:`75`)

-   Removed official support for Python 3.7 (:gh:`72`)

-   Improved performance of ``itemloaders.utils.arg_to_iter`` (:gh:`51`)

-   Fixed test expectations on recent Python versions (:gh:`77`)

-   Improved CI (:gh:`78`)

.. _release-1.1.0:

itemloaders 1.1.0 (2023-04-21)
------------------------------

-   Added JMESPath support (:meth:`ItemLoader.add_jmes` etc.), requiring Parsel
    1.8.1+ (:gh:`68`)

-   Added official support for Python 3.11 (:gh:`59`)

-   Removed official support for Python 3.6 (:gh:`61`)

-   Internal code cleanup (:gh:`65`, :gh:`66`)

-   Added ``pre-commit`` support and applied changes from ``black`` and
    ``flake8`` (:gh:`70`).

-   Improved CI (:gh:`60`)

.. _release-1.0.6:

itemloaders 1.0.6 (2022-08-29)
------------------------------

-   Fixes a regression introduced in 1.0.5 that would cause the ``re`` parameter of
    :meth:`ItemLoader.add_xpath` and similar methods to be passed to lxml, which
    would trigger an exception when the value of ``re`` was a compiled pattern and
    not a string (:gh:`56`)

.. _release-1.0.5:

itemloaders 1.0.5 (2022-08-25)
------------------------------

-  Allow additional args to be passed when calling :meth:`ItemLoader.add_xpath` (:gh:`48`)

-  Fixed missing space in an exception message (:gh:`47`)

-  Updated company name in author and copyright sections (:gh:`42`)

-  Added official support for Python 3.9 and improved PyPy compatibility (:gh:`44`)

-  Added official support for Python 3.10 (:gh:`53`)

.. _release-1.0.4:

itemloaders 1.0.4 (2020-11-12)
------------------------------

-   When adding a :class:`scrapy.Item` object as a value into an
    :class:`ItemLoader` object, that item is now added *as is*, instead of
    becoming a :class:`list` of keys from its :attr:`scrapy.Item.fields`
    (:gh:`28`, :gh:`29`)

-   Increased test coverage (:gh:`27`)


.. _release-1.0.3:

itemloaders 1.0.3 (2020-09-09)
------------------------------

-   Calls to :meth:`ItemLoader.get_output_value` no longer affect the output of
    :meth:`ItemLoader.load_item` (:gh:`21`, :gh:`22`)

-   Fixed some documentation links (:gh:`19`, :gh:`23`)

-   Fixed some test warnings (:gh:`24`)


.. _release-1.0.2:

itemloaders 1.0.2 (2020-08-05)
------------------------------

-   Included the license file in the source releases (:gh:`13`)

-   Cleaned up some remnants of Python 2 (:gh:`16`, :gh:`17`)


.. _release-1.0.1:

itemloaders 1.0.1 (2020-07-02)
------------------------------

-   Extended item type support to all item types supported by itemadapter_
    (:gh:`13`)

-   :ref:`Input and output processors <declaring-loaders>` defined in item
    field metadata are now taken into account (:gh:`13`)

-   Lowered some minimum dependency versions (:gh:`10`):

    -   ``parsel``: 1.5.2 → 1.5.0

    -   ``w3lib``: 1.21.0 → 1.17.0

-   Improved the README file (:gh:`9`)

-   Improved continuous integration (:gh:`e62d95b`)


.. _release-1.0.0:

itemloaders 1.0.0 (2020-05-18)
------------------------------

-   Initial release, based on a part of the :doc:`Scrapy <scrapy:index>` code base.


.. _itemadapter: https://github.com/scrapy/itemadapter#itemadapter
