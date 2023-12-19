"""
Copy/paste from scrapy source at the moment, to ensure tests are working.
Refactoring to come later
"""
import inspect
from functools import partial
from typing import Generator


def arg_to_iter(arg):
    """Return an iterable based on *arg*.

    If *arg* is a list, a tuple or a generator, it will be returned as is.

    If *arg* is ``None``, an empty list will be returned.

    If *arg* is anything else, a list will be returned with *arg* as its only
    item, i.e. ``[arg]``.
    """
    if arg is None:
        return []
    if isinstance(arg, (list, tuple, Generator)):
        return arg
    return [arg]


def get_func_args(func, stripself=False):
    """Return the argument name list of a callable"""
    if inspect.isfunction(func):
        spec = inspect.getfullargspec(func)
        func_args = spec.args + spec.kwonlyargs
    elif inspect.isclass(func):
        return get_func_args(func.__init__, True)
    elif inspect.ismethod(func):
        return get_func_args(func.__func__, True)
    elif inspect.ismethoddescriptor(func):
        return []
    elif isinstance(func, partial):
        return [x for x in get_func_args(func.func)[len(func.args):]
                if not (func.keywords and x in func.keywords)]
    elif hasattr(func, '__call__'):
        if inspect.isroutine(func):
            return []
        elif getattr(func, '__name__', None) == '__call__':
            return []
        else:
            return get_func_args(func.__call__, True)
    else:
        raise TypeError(f'{type(func)} is not callable')
    if stripself:
        func_args.pop(0)
    return func_args


def _getargspec_py23(func):
    """_getargspec_py23(function) -> named tuple ArgSpec(args, varargs, keywords,
                                                        defaults)

    Was identical to inspect.getargspec() in python2, but uses
    inspect.getfullargspec() for python3 behind the scenes to avoid
    DeprecationWarning.

    >>> def f(a, b=2, *ar, **kw):
    ...     pass

    >>> _getargspec_py23(f)
    ArgSpec(args=['a', 'b'], varargs='ar', keywords='kw', defaults=(2,))
    """
    return inspect.ArgSpec(*inspect.getfullargspec(func)[:4])
