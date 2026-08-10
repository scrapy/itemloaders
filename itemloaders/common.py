"""Common functions used in Item Loaders code"""

from __future__ import annotations

from functools import lru_cache, partial
from typing import TYPE_CHECKING, Any

from itemloaders.utils import get_func_args

if TYPE_CHECKING:
    from collections.abc import Callable, MutableMapping


@lru_cache(maxsize=1024)
def _takes_loader_context(function: Callable[..., Any]) -> bool:
    return "loader_context" in get_func_args(function)


def wrap_loader_context(
    function: Callable[..., Any], context: MutableMapping[str, Any]
) -> Callable[..., Any]:
    """Wrap functions that receive loader_context to contain the context
    "pre-loaded" and expose an interface that receives only one argument
    """
    try:
        takes_loader_context = _takes_loader_context(function)
    except TypeError:  # unhashable function
        takes_loader_context = "loader_context" in get_func_args(function)
    if takes_loader_context:
        return partial(function, loader_context=context)
    return function
