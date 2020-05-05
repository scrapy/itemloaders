.. _nested-loaders:

Nested Loaders
==============

When parsing related values from a subsection of a document, it can be
useful to create nested loaders.  Imagine you're extracting details from
a footer of a page that looks something like:

Example::

    <footer>
        <a class="social" href="https://facebook.com/whatever">Like Us</a>
        <a class="social" href="https://twitter.com/whatever">Follow Us</a>
        <a class="email" href="mailto:whatever@example.com">Email Us</a>
    </footer>

Without nested loaders, you need to specify the full xpath (or css) for each value
that you wish to extract.

Example::

    loader = ItemLoader()
    # load stuff not in the footer
    loader.add_xpath('social', '//footer/a[@class = "social"]/@href')
    loader.add_xpath('email', '//footer/a[@class = "email"]/@href')
    loader.load_item()

Instead, you can create a nested loader with the footer selector and add values
relative to the footer.  The functionality is the same but you avoid repeating
the footer selector.

Example::

    loader = ItemLoader()
    # load stuff not in the footer
    footer_loader = loader.nested_xpath('//footer')
    footer_loader.add_xpath('social', 'a[@class = "social"]/@href')
    footer_loader.add_xpath('email', 'a[@class = "email"]/@href')
    # no need to call footer_loader.load_item()
    loader.load_item()

You can nest loaders arbitrarily and they work with either xpath or css selectors.
As a general guideline, use nested loaders when they make your code simpler but do
not go overboard with nesting or your parser can become difficult to read.
