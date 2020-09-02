.. currentmodule:: itemloaders

.. _processors:

Input and Output processors
===========================

An Item Loader contains one input processor and one output processor for each
(item) field. The input processor processes the extracted data as soon as it's
received (through the :meth:`~ItemLoader.add_xpath`, :meth:`~ItemLoader.add_css` or
:meth:`~ItemLoader.add_value` methods) and the result of the input processor is
collected and kept inside the ItemLoader. After collecting all data, the
:meth:`ItemLoader.load_item` method is called to populate and get the populated
item object.  That's when the output processor is
called with the data previously collected (and processed using the input
processor). The result of the output processor is the final value that gets
assigned to the item.

Let's see an example to illustrate how the input and output processors are
called for a particular field (the same applies for any other field)::

    l = ItemLoader(selector=some_selector)
    l.add_xpath('name', xpath1) # (1)
    l.add_xpath('name', xpath2) # (2)
    l.add_css('name', css) # (3)
    l.add_value('name', 'test') # (4)
    return l.load_item() # (5)

So what happens is:

1. Data from ``xpath1`` is extracted, and passed through the *input processor* of
   the ``name`` field. The result of the input processor is collected and kept in
   the Item Loader (but not yet assigned to the item).

2. Data from ``xpath2`` is extracted, and passed through the same *input
   processor* used in (1). The result of the input processor is appended to the
   data collected in (1) (if any).

3. This case is similar to the previous ones, except that the data is extracted
   from the ``css`` CSS selector, and passed through the same *input
   processor* used in (1) and (2). The result of the input processor is appended to the
   data collected in (1) and (2) (if any).

4. This case is also similar to the previous ones, except that the value to be
   collected is assigned directly, instead of being extracted from a XPath
   expression or a CSS selector.
   However, the value is still passed through the input processors. In this
   case, since the value is not iterable it is converted to an iterable of a
   single element before passing it to the input processor, because input
   processor always receive iterables.

5. The data collected in steps (1), (2), (3) and (4) is passed through
   the *output processor* of the ``name`` field.
   The result of the output processor is the value assigned to the ``name``
   field in the item.

It's worth noticing that processors are just callable objects, which are called
with the data to be parsed, and return a parsed value. So you can use any
function as input or output processor. The only requirement is that they must
accept one (and only one) positional argument, which will be an iterable.

.. note:: Both input and output processors must receive an iterable as their
   first argument. The output of those functions can be anything. The result of
   input processors will be appended to an internal list (in the Loader)
   containing the collected values (for that field). The result of the output
   processors is the value that will be finally assigned to the item.

The other thing you need to keep in mind is that the values returned by input
processors are collected internally (in lists) and then passed to output
processors to populate the fields.

Last, but not least, ``itemloaders`` comes with some :ref:`commonly used processors
<built-in-processors>` built-in for convenience.
