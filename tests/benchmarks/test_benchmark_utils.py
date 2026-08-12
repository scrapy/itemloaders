from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import pytest

from itemloaders.utils import arg_to_iter

if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture

# Each round calls the function this many times, so that the measurement
# reflects the function itself rather than the benchmark call overhead.
CALLS_PER_ROUND = 100


@dataclass
class DataclassItem:
    foo: str


CASES: dict[str, Any] = {
    "none": None,
    "int": 1,
    "str": "foo",
    "bytes": b"foo",
    "list": ["foo", "bar"],
    "tuple": ("foo", "bar"),
    "generator": (letter for letter in "foobar"),
    "iterator": iter(["foo", "bar"]),
    "map": map(str.title, ["foo", "bar"]),
    "range": range(2),
    "set": {"foo", "bar"},
    "frozenset": frozenset({"foo", "bar"}),
    "dict": {"foo": "bar"},
    "dict_keys": {"foo": "bar"}.keys(),
    "dict_values": {"foo": "bar"}.values(),
    "dict_items": {"foo": "bar"}.items(),
    "dataclass_item": DataclassItem(foo="bar"),
}

try:
    import attr
except ImportError:
    pass
else:

    @attr.s
    class AttrsItem:
        foo = attr.ib()

    CASES["attrs_item"] = AttrsItem(foo="bar")

try:
    from scrapy import Field, Item
except ImportError:
    pass
else:

    class ScrapyItem(Item):
        foo = Field()

    CASES["scrapy_item"] = ScrapyItem(foo="bar")


@pytest.mark.parametrize("case", CASES)
def test_arg_to_iter(benchmark: BenchmarkFixture, case: str) -> None:
    value = CASES[case]

    @benchmark
    def factory() -> None:
        for _ in range(CALLS_PER_ROUND):
            arg_to_iter(value)
