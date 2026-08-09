"""
Copy/paste from scrapy source at the moment, to ensure tests are working.
Refactoring to come later
"""

from __future__ import annotations

import inspect
from abc import get_cache_token
from collections.abc import Callable, Iterable, Iterator
from collections.abc import Set as AbstractSet
from functools import partial
from typing import Any

# Whether each class seen so far is one that arg_to_iter returns as is. Testing
# a class against an abstract base class costs an order of magnitude more than
# a dictionary lookup, so each class is only tested once.
_iterable_classes: dict[type, bool] = {}
_abc_cache_token = get_cache_token()

# Reaching this many entries means classes are being created dynamically, and
# caching a result per class would grow the cache without bound.
_MAX_ITERABLE_CLASSES = 1000


def _is_iterable_class(cls: type) -> bool:
    """Tell whether :func:`arg_to_iter` should return instances of *cls* as is,
    caching the result for later calls.

    Only call this for classes that are not already cached as iterable.
    """
    global _abc_cache_token  # noqa: PLW0603  # pylint: disable=global-statement

    # Registering a class against an abstract base class turns a negative
    # result into a positive one, so only negative results can go stale, and
    # only until the next registration bumps the token.
    token = get_cache_token()
    if token != _abc_cache_token:
        _iterable_classes.clear()
        _abc_cache_token = token
    elif cls in _iterable_classes:
        return False

    if len(_iterable_classes) >= _MAX_ITERABLE_CLASSES:
        _iterable_classes.clear()
    result = issubclass(cls, (list, tuple, Iterator, AbstractSet))
    _iterable_classes[cls] = result
    return result


def arg_to_iter(arg: Any) -> Iterable[Any]:
    """Return an iterable based on *arg*.

    If *arg* is a :class:`list`, a :class:`tuple`, a
    :class:`~collections.abc.Set` or an :class:`~collections.abc.Iterator`, it
    will be returned as is.

    If *arg* is ``None``, an empty list will be returned.

    If *arg* is anything else, a list will be returned with *arg* as its only
    item, i.e. ``[arg]``.
    """
    if arg is None:
        return []
    cls = arg.__class__
    if _iterable_classes.get(cls) or _is_iterable_class(cls):
        return arg  # type: ignore[no-any-return]
    return [arg]


def get_func_args(func: Callable[..., Any], stripself: bool = False) -> list[str]:
    """Return the argument name list of a callable object"""
    if not callable(func):
        raise TypeError(f"func must be callable, got {type(func).__name__!r}")

    args: list[str] = []
    try:
        sig = inspect.signature(func)
    except ValueError:
        return args

    if isinstance(func, partial):
        partial_args = func.args
        partial_kw = func.keywords

        for name, param in sig.parameters.items():
            if param.name in partial_args:
                continue
            if partial_kw and param.name in partial_kw:
                continue
            args.append(name)
    else:
        args = list(sig.parameters)

    if stripself and args and args[0] == "self":
        args = args[1:]
    return args
