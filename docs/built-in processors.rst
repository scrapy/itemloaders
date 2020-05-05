.. _built-in processors:

Available built-in processors
=============================

.. module:: itemloaders.processors
   :synopsis: A collection of processors to use with Item Loaders

Even though you can use any callable function as input and output processors,
``itemloaders`` provides some commonly used processors, which are described below. Some
of them, like the :class:`MapCompose` (which is typically used as input
processor) compose the output of several functions executed in order, to
produce the final parsed value.

Here is a list of all built-in processors:

.. class:: Identity

    The simplest processor, which doesn't do anything. It returns the original
    values unchanged. It doesn't receive any ``__init__`` method arguments, nor does it
    accept Loader contexts.

    Example:

    >>> from itemloaders.processors import Identity
    >>> proc = Identity()
    >>> proc(['one', 'two', 'three'])
    ['one', 'two', 'three']

.. class:: TakeFirst

    Returns the first non-null/non-empty value from the values received,
    so it's typically used as an output processor to single-valued fields.
    It doesn't receive any ``__init__`` method arguments, nor does it accept Loader contexts.

    Example:

    >>> from itemloaders.processors import TakeFirst
    >>> proc = TakeFirst()
    >>> proc(['', 'one', 'two', 'three'])
    'one'

.. class:: Join(separator=u' ')

    Returns the values joined with the separator given in the ``__init__`` method, which
    defaults to ``u' '``. It doesn't accept Loader contexts.

    When using the default separator, this processor is equivalent to the
    function: ``u' '.join``

    Examples:

    >>> from itemloaders.processors import Join
    >>> proc = Join()
    >>> proc(['one', 'two', 'three'])
    'one two three'
    >>> proc = Join('<br>')
    >>> proc(['one', 'two', 'three'])
    'one<br>two<br>three'

.. class:: Compose(\*functions, \**default_loader_context)

    A processor which is constructed from the composition of the given
    functions. This means that each input value of this processor is passed to
    the first function, and the result of that function is passed to the second
    function, and so on, until the last function returns the output value of
    this processor.

    By default, stop process on ``None`` value. This behaviour can be changed by
    passing keyword argument ``stop_on_none=False``.

    Example:

    >>> from itemloaders.processors import Compose
    >>> proc = Compose(lambda v: v[0], str.upper)
    >>> proc(['hello', 'world'])
    'HELLO'

    Each function can optionally receive a ``loader_context`` parameter. For
    those which do, this processor will pass the currently active :ref:`Loader
    context <loaders-context>` through that parameter.

    The keyword arguments passed in the ``__init__`` method are used as the default
    Loader context values passed to each function call. However, the final
    Loader context values passed to functions are overridden with the currently
    active Loader context accessible through the :meth:`ItemLoader.context`
    attribute.

.. class:: MapCompose(\*functions, \**default_loader_context)

    A processor which is constructed from the composition of the given
    functions, similar to the :class:`Compose` processor. The difference with
    this processor is the way internal results are passed among functions,
    which is as follows:

    The input value of this processor is *iterated* and the first function is
    applied to each element. The results of these function calls (one for each element)
    are concatenated to construct a new iterable, which is then used to apply the
    second function, and so on, until the last function is applied to each
    value of the list of values collected so far. The output values of the last
    function are concatenated together to produce the output of this processor.

    Each particular function can return a value or a list of values, which is
    flattened with the list of values returned by the same function applied to
    the other input values. The functions can also return ``None`` in which
    case the output of that function is ignored for further processing over the
    chain.

    This processor provides a convenient way to compose functions that only
    work with single values (instead of iterables). For this reason the
    :class:`MapCompose` processor is typically used as input processor, since
    data is often extracted using the
    :meth:`~parsel.Selector.extract` method of `parsel selectors`_,
    which returns a list of unicode strings.

    The example below should clarify how it works:

    >>> def filter_world(x):
    ...     return None if x == 'world' else x
    ...
    >>> from itemloaders.processors import MapCompose
    >>> proc = MapCompose(filter_world, str.upper)
    >>> proc(['hello', 'world', 'this', 'is', 'something'])
    ['HELLO, 'THIS', 'IS', 'SOMETHING']

    As with the Compose processor, functions can receive Loader contexts, and
    ``__init__`` method keyword arguments are used as default context values. See
    :class:`Compose` processor for more info.

.. class:: SelectJmes(json_path)

    Queries the value using the json path provided to the ``__init__`` method and returns the output.
    Requires jmespath (https://github.com/jmespath/jmespath.py) to run.
    This processor takes only one input at a time.

    Example:

    >>> from itemloaders.processors import SelectJmes, Compose, MapCompose
    >>> proc = SelectJmes("foo") #for direct use on lists and dictionaries
    >>> proc({'foo': 'bar'})
    'bar'
    >>> proc({'foo': {'bar': 'baz'}})
    {'bar': 'baz'}

    Working with Json:

    >>> import json
    >>> proc_single_json_str = Compose(json.loads, SelectJmes("foo"))
    >>> proc_single_json_str('{"foo": "bar"}')
    'bar'
    >>> proc_json_list = Compose(json.loads, MapCompose(SelectJmes('foo')))
    >>> proc_json_list('[{"foo":"bar"}, {"baz":"tar"}]')
    ['bar']

.. _`parsel selectors`: https://parsel.readthedocs.io/en/latest/parsel.html#parsel.selector.Selector.extract
