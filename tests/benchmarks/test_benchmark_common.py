from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

import pytest

from itemloaders.common import wrap_loader_context

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture

# Each round calls the function this many times, so that the measurement
# reflects the function itself rather than the benchmark call overhead.
CALLS_PER_ROUND = 100

CONTEXT: dict[str, Any] = {"encoding": "utf-8"}


def _function(value: str, chars: str = " ", loader_context: Any = None) -> str:
    return value.strip(chars)


class _Processor:
    def __call__(self, value: str, loader_context: Any = None) -> str:
        return value.strip()

    def method(self, value: str) -> str:
        return value.strip()


class _UnhashableProcessor(_Processor):
    __hash__ = None  # type: ignore[assignment]


_processor = _Processor()

CASES: dict[str, Any] = {
    "function": _function,
    "partial": partial(_function, chars="-"),
    "method": _processor.method,
    "processor": _processor,
    "unhashable_processor": _UnhashableProcessor(),
    "type": float,
    "method_descriptor": str.strip,
}


@pytest.mark.parametrize("case", CASES)
def test_wrap_loader_context(benchmark: BenchmarkFixture, case: str) -> None:
    function = CASES[case]

    @benchmark
    def factory() -> None:
        for _ in range(CALLS_PER_ROUND):
            wrap_loader_context(function, CONTEXT)
