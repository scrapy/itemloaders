===========
itemloaders
===========

.. image:: https://img.shields.io/pypi/v/itemloaders.svg
   :target: https://pypi.python.org/pypi/itemloaders
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/itemloaders.svg
   :target: https://pypi.python.org/pypi/itemloaders
   :alt: Supported Python Versions

.. image:: https://travis-ci.com/scrapy/itemloaders.svg?branch=master
   :target: https://travis-ci.com/scrapy/itemloaders
   :alt: Build Status

.. image:: https://codecov.io/github/scrapy/itemloaders/coverage.svg?branch=master
   :target: https://codecov.io/gh/scrapy/scrapy
   :alt: Coverage report

.. image:: https://readthedocs.org/projects/itemloaders/badge/?version=latest
   :target: https://itemloaders.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


``itemloaders`` is a library that helps you collect data into models.
It's specially useful when you need to standardize the data from many sources.
For example, it allows you to have all your casting and parsing rules in a
single place.
Also, it comes in handy to extract data from web pages, as it supports
data extraction using CSS and XPath Selectors.

Here is an example to get you started::

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

For more information, check out the `documentation <https://itemloaders.readthedocs.io/en/latest/>`_.

========================
Contributing/Maintaining
========================

All contributions are welcome!

* If you can to review some code, check open
`Pull Requests here <https://github.com/scrapy/itemloaders/pulls>`_


* If you want to submit a code change
* File an `issue here <https://github.com/scrapy/itemloaders/issues>`_, if there isn't one yet
* Fork this repository
* Create a branch to work on your changes
* Push your local branch and submit a Pull Request

* New versions are published automatically to PyPi
    * The ``master`` branch must succeed in Travis CI
    * Update ``setup.py`` with the new version
    * Tag the commit
    * Push tags
