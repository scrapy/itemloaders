from typing import Any

from itemloaders.common import wrap_loader_context

CONTEXT: dict[str, Any] = {"encoding": "utf-8"}


class Processor:
    __hash__ = None  # type: ignore[assignment]

    def __call__(self, value: str, loader_context: Any = None) -> Any:
        return loader_context


def test_unhashable_function():
    assert wrap_loader_context(Processor(), CONTEXT)("foo") == CONTEXT
