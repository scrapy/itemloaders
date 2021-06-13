"""
Item Loader

See documentation in docs/topics/loaders.rst
"""
from contextlib import suppress

from itemadapter import ItemAdapter
from parsel.utils import extract_regex, flatten

from itemloaders.common import wrap_loader_context
from itemloaders.processors import Identity
from itemloaders.utils import arg_to_iter


def unbound_method(method):
    """
    Allow to use single-argument functions as input or output processors
    (no need to define an unused first 'self' argument)
    """
    with suppress(AttributeError):
        if '.' not in method.__qualname__:
            return method.__func__
    return method


class ItemLoader:
    """
    Return a new Item Loader for populating the given item. If no item is
    given, one is instantiated automatically using the class in
    :attr:`default_item_class`.

    When instantiated with a :param ``selector`` parameter the :class:`ItemLoader` class
    provides convenient mechanisms for extracting data from web pages
    using parsel_ selectors.

    :param item: The item instance to populate using subsequent calls to
        :meth:`~ItemLoader.add_xpath`, :meth:`~ItemLoader.add_css`,
        or :meth:`~ItemLoader.add_value`.
    :type item: :class:`dict` object

    :param selector: The selector to extract data from, when using the
        :meth:`add_xpath` (resp. :meth:`add_css`) or :meth:`replace_xpath`
        (resp. :meth:`replace_css`) method.
    :type selector: :class:`~parsel.selector.Selector` object

    The item, selector and the remaining keyword arguments are
    assigned to the Loader context (accessible through the :attr:`context` attribute).

    .. attribute:: item

        The item object being parsed by this Item Loader.
        This is mostly used as a property so when attempting to override this
        value, you may want to check out :attr:`default_item_class` first.

    .. attribute:: context

        The currently active :ref:`Context <loaders-context>` of this Item Loader.
        Refer to <loaders-context> for more information about the Loader Context.

    .. attribute:: default_item_class

        An Item class (or factory), used to instantiate items when not given in
        the ``__init__`` method.

        .. warning:: Currently, this factory/class needs to be
            callable/instantiated without any arguments.
            If you are using ``dataclasses``, please consider the following
            alternative::

                from dataclasses import dataclass, field
                from typing import Optional

                @dataclass
                class Product:
                    name: Optional[str] = field(default=None)
                    price: Optional[float] = field(default=None)

    .. attribute:: default_input_processor

        The default input processor to use for those fields which don't specify
        one.

    .. attribute:: default_output_processor

        The default output processor to use for those fields which don't specify
        one.

    .. attribute:: selector

        The :class:`~parsel.selector.Selector` object to extract data from.
        It's the selector given in the ``__init__`` method.
        This attribute is meant to be read-only.

    .. _parsel: https://parsel.readthedocs.io/en/latest/
    """

    default_item_class = dict
    default_input_processor = Identity()
    default_output_processor = Identity()

    def __init__(self, item=None, selector=None, parent=None, stats=None, **context):
        self.selector = selector
        context.update(selector=selector)
        if item is None:
            item = self.default_item_class()
        self._local_item = item
        context['item'] = item
        self.context = context
        self.parent = parent
        self._local_values = {}
        # values from initial item
        for field_name, value in ItemAdapter(item).items():
            self._values.setdefault(field_name, [])
            self._values[field_name] += arg_to_iter(value)

        # This is the new injected dependency that we'll be using as the main
        # functionality of this tool.
        self.stats = stats

        # This keeps track of the position of the 'field' name that is being
        # loaded for a more accurate logging in the stats.
        self.field_position_tracker = defaultdict(int)

    @property
    def _values(self):
        if self.parent is not None:
            return self.parent._values
        else:
            return self._local_values

    @property
    def item(self):
        if self.parent is not None:
            return self.parent.item
        else:
            return self._local_item

    def nested_xpath(self, xpath, **context):
        """
        Create a nested loader with an xpath selector.
        The supplied selector is applied relative to selector associated
        with this :class:`ItemLoader`. The nested loader shares the item
        with the parent :class:`ItemLoader` so calls to :meth:`add_xpath`,
        :meth:`add_value`, :meth:`replace_value`, etc. will behave as expected.
        """
        selector = self.selector.xpath(xpath)
        context.update(selector=selector)
        subloader = self.__class__(
            item=self.item, parent=self, **context
        )
        return subloader

    def nested_css(self, css, **context):
        """
        Create a nested loader with a css selector.
        The supplied selector is applied relative to selector associated
        with this :class:`ItemLoader`. The nested loader shares the item
        with the parent :class:`ItemLoader` so calls to :meth:`add_xpath`,
        :meth:`add_value`, :meth:`replace_value`, etc. will behave as expected.
        """
        selector = self.selector.css(css)
        context.update(selector=selector)
        subloader = self.__class__(
            item=self.item, parent=self, **context
        )
        return subloader

    def add_value(self, field_name, value, *processors, **kw):
        """
        Process and then add the given ``value`` for the given field.

        The value is first passed through :meth:`get_value` by giving the
        ``processors`` and ``kwargs``, and then passed through the
        :ref:`field input processor <processors>` and its result
        appended to the data collected for that field. If the field already
        contains collected data, the new data is added.

        The given ``field_name`` can be ``None``, in which case values for
        multiple fields may be added. And the processed value should be a dict
        with field_name mapped to values.

        Examples::

            loader.add_value('name', 'Color TV')
            loader.add_value('colours', ['white', 'blue'])
            loader.add_value('length', '100')
            loader.add_value('name', 'name: foo', TakeFirst(), re='name: (.+)')
            loader.add_value(None, {'name': 'foo', 'sex': 'male'})
        """
        value = self.get_value(value, *processors, **kw)
        if value is None:
            return
        if not field_name:
            for k, v in value.items():
                self._add_value(k, v)
        else:
            self._add_value(field_name, value)

    def replace_value(self, field_name, value, *processors, **kw):
        """
        Similar to :meth:`add_value` but replaces the collected data with the
        new value instead of adding it.
        """
        value = self.get_value(value, *processors, **kw)
        if value is None:
            return
        if not field_name:
            for k, v in value.items():
                self._replace_value(k, v)
        else:
            self._replace_value(field_name, value)

    def _add_value(self, field_name, value):
        value = arg_to_iter(value)
        processed_value = self._process_input_value(field_name, value)
        if processed_value:
            self._values.setdefault(field_name, [])
            self._values[field_name] += arg_to_iter(processed_value)

    def _replace_value(self, field_name, value):
        self._values.pop(field_name, None)
        self._add_value(field_name, value)

    def get_value(self, value, *processors, **kw):
        """
        Process the given ``value`` by the given ``processors`` and keyword
        arguments.

        Available keyword arguments:

        :param re: a regular expression to use for extracting data from the
            given value using :func:`~parsel.utils.extract_regex` method,
            applied before processors
        :type re: str or typing.Pattern

        Examples:

        >>> from itemloaders import ItemLoader
        >>> from itemloaders.processors import TakeFirst
        >>> loader = ItemLoader()
        >>> loader.get_value('name: foo', TakeFirst(), str.upper, re='name: (.+)')
        'FOO'
        """
        regex = kw.get('re', None)
        if regex:
            value = arg_to_iter(value)
            value = flatten(extract_regex(regex, x) for x in value)

        for proc in processors:
            if value is None:
                break
            _proc = proc
            proc = wrap_loader_context(proc, self.context)
            try:
                value = proc(value)
            except Exception as e:
                raise ValueError("Error with processor %s value=%r error='%s: %s'" %
                                 (_proc.__class__.__name__, value,
                                  type(e).__name__, str(e)))
        return value

    def load_item(self):
        """
        Populate the item with the data collected so far, and return it. The
        data collected is first passed through the :ref:`output processors
        <processors>` to get the final value to assign to each item field.
        """
        adapter = ItemAdapter(self.item)
        for field_name in tuple(self._values):
            value = self.get_output_value(field_name)
            if value is not None:
                adapter[field_name] = value

        return adapter.item

    def get_output_value(self, field_name):
        """
        Return the collected values parsed using the output processor, for the
        given field. This method doesn't populate or modify the item at all.
        """
        proc = self.get_output_processor(field_name)
        proc = wrap_loader_context(proc, self.context)
        value = self._values.get(field_name, [])
        try:
            return proc(value)
        except Exception as e:
            raise ValueError("Error with output processor: field=%r value=%r error='%s: %s'" %
                             (field_name, value, type(e).__name__, str(e)))

    def get_collected_values(self, field_name):
        """Return the collected values for the given field."""
        return self._values.get(field_name, [])

    def get_input_processor(self, field_name):
        proc = getattr(self, '%s_in' % field_name, None)
        if not proc:
            proc = self._get_item_field_attr(
                field_name,
                'input_processor',
                self.default_input_processor
            )
        return unbound_method(proc)

    def get_output_processor(self, field_name):
        proc = getattr(self, '%s_out' % field_name, None)
        if not proc:
            proc = self._get_item_field_attr(
                field_name,
                'output_processor',
                self.default_output_processor
            )
        return unbound_method(proc)

    def _get_item_field_attr(self, field_name, key, default=None):
        field_meta = ItemAdapter(self.item).get_field_meta(field_name)
        return field_meta.get(key, default)

    def _process_input_value(self, field_name, value):
        proc = self.get_input_processor(field_name)
        _proc = proc
        proc = wrap_loader_context(proc, self.context)
        try:
            return proc(value)
        except Exception as e:
            raise ValueError(
                "Error with input processor %s: field=%r value=%r "
                "error='%s: %s'" % (_proc.__class__.__name__, field_name,
                                    value, type(e).__name__, str(e)))

    def _check_selector_method(self):
        if self.selector is None:
            raise RuntimeError(
                "To use XPath or CSS selectors, %s "
                "must be instantiated with a selector" % self.__class__.__name__
            )

    def add_xpath(self, field_name, xpath, *processors, **kw):
        """
        Similar to :meth:`ItemLoader.add_value` but receives an XPath instead of a
        value, which is used to extract a list of strings from the
        selector associated with this :class:`ItemLoader`.

        See :meth:`get_xpath` for ``kwargs``.

        :param xpath: the XPath to extract data from
        :type xpath: str

        Examples::

            # HTML snippet: <p class="product-name">Color TV</p>
            loader.add_xpath('name', '//p[@class="product-name"]')
            # HTML snippet: <p id="price">the price is $1200</p>
            loader.add_xpath('price', '//p[@id="price"]', re='the price is (.*)')

        """
        self.field_position_tracker[f"{field_name}_xpath"] += 1
        values = self.get_selector_values(field_name, xpath, 'xpath', **kw)
        self.add_value(field_name, values, *processors, **kw)

    def replace_xpath(self, field_name, xpath, *processors, **kw):
        """
        Similar to :meth:`add_xpath` but replaces collected data instead of adding it.
        """
        values = self.get_selector_values(field_name, xpath, 'xpath', **kw)
        self.replace_value(field_name, values, *processors, **kw)

    def get_xpath(self, xpath, *processors, **kw):
        """
        Similar to :meth:`ItemLoader.get_value` but receives an XPath instead of a
        value, which is used to extract a list of unicode strings from the
        selector associated with this :class:`ItemLoader`.

        :param xpath: the XPath to extract data from
        :type xpath: str

        :param re: a regular expression to use for extracting data from the
            selected XPath region
        :type re: str or typing.Pattern

        Examples::

            # HTML snippet: <p class="product-name">Color TV</p>
            loader.get_xpath('//p[@class="product-name"]')
            # HTML snippet: <p id="price">the price is $1200</p>
            loader.get_xpath('//p[@id="price"]', TakeFirst(), re='the price is (.*)')

        """
        values = self.get_selector_values(None, xpath, 'xpath', **kw)
        return self.get_value(values, *processors, **kw)

    def add_css(self, field_name, css, *processors, **kw):
        """
        Similar to :meth:`ItemLoader.add_value` but receives a CSS selector
        instead of a value, which is used to extract a list of unicode strings
        from the selector associated with this :class:`ItemLoader`.

        See :meth:`get_css` for ``kwargs``.

        :param css: the CSS selector to extract data from
        :type css: str

        Examples::

            # HTML snippet: <p class="product-name">Color TV</p>
            loader.add_css('name', 'p.product-name')
            # HTML snippet: <p id="price">the price is $1200</p>
            loader.add_css('price', 'p#price', re='the price is (.*)')
        """
        self.field_position_tracker[f"{field_name}_css"] += 1
        values = self.get_selector_values(field_name, css, 'css', **kw)
        self.add_value(field_name, values, *processors, **kw)

    def replace_css(self, field_name, css, *processors, **kw):
        """
        Similar to :meth:`add_css` but replaces collected data instead of adding it.
        """
        values = self.get_selector_values(field_name, css, 'css', **kw)
        self.replace_value(field_name, values, *processors, **kw)

    def get_css(self, css, *processors, **kw):
        """
        Similar to :meth:`ItemLoader.get_value` but receives a CSS selector
        instead of a value, which is used to extract a list of unicode strings
        from the selector associated with this :class:`ItemLoader`.

        :param css: the CSS selector to extract data from
        :type css: str

        :param re: a regular expression to use for extracting data from the
            selected CSS region
        :type re: str or typing.Pattern

        Examples::

            # HTML snippet: <p class="product-name">Color TV</p>
            loader.get_css('p.product-name')
            # HTML snippet: <p id="price">the price is $1200</p>
            loader.get_css('p#price', TakeFirst(), re='the price is (.*)')
        """
        values = self.get_selector_values(None, css, 'css', **kw)
        return self.get_value(values, *processors, **kw)

    def get_selector_values(self, field_name, selector_rules, selector_type, **kw):

        self._check_selector_method()

        selector = getattr(self.selector, selector_type or '', None)

        # The optional arg in methods like `add_css()` for context in stats
        name = kw.get("name")

        # For every call of `add_css()` and `add_xpath()` this is incremented.
        # We'll use it as the base index of the position of the logged stats.
        index = self.field_position_tracker[f"{field_name}_{selector_type}"]

        values = []
        for position, rule in enumerate(arg_to_iter(selector_rules), index):
            parsed_data = selector(rule).getall()
            values.append(parsed_data)
            self.write_to_stats(
                field_name, parsed_data, position, selector_type, name=name
            )
        return flatten(values)

    def write_to_stats(
        self, field_name, parsed_data, position, selector_type, name=None
    ):
        """Responsible for logging the parser rules usage.

        The implementation below where each missing parsed_data is being logged
        to the stat is clunky, but necessary. With this, we can only surmise
        that it's safe to remove parser fallback parser if it's all just
        '.../missing' in the stats.
        """

        if not self.stats or not field_name:
            return

        parser_label = (
            f"parser/{self.loader_name}/{field_name}/{selector_type}/{position}"
        )

        if name:
            parser_label += f"/{name}"

        if parsed_data in (None, []):
            parser_label += "/missing"

        self.stats.inc_value(parser_label)

    @property
    def loader_name(self):
        return self.__class__.__name__
