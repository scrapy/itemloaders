.. currentmodule:: itemloaders

.. _release-notes:

Release notes
=============

.. _release-1.0.3:

itemloaders 1.0.3 (2020-09-NN)
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

    -   :doc:`parsel <parsel:index>`: 1.5.2 → 1.5.0

    -   :doc:`w3lib <w3lib:index>`: 1.21.0 → 1.17.0

-   Improved the README file (:gh:`9`)

-   Improved continuous integration (:gh:`e62d95b`)


.. _release-1.0.0:

itemloaders 1.0.0 (2020-05-18)
------------------------------

Initial release, based on a part of the :doc:`Scrapy <scrapy:index>` code base.


.. _itemadapter: https://github.com/scrapy/itemadapter#itemadapter
