from collections.abc import Iterator
from functools import partial

import pytest

from itemloaders import ItemLoader
from itemloaders.processors import (
    Compose,
    Identity,
    Join,
    MapCompose,
    TakeFirst,
    TakeFirstN,
)


def test_take_first():
    proc = TakeFirst()
    assert proc([None, "", "hello", "world"]) == "hello"
    assert proc([None, "", 0, "hello", "world"]) == 0


def test_identity():
    proc = Identity()
    assert proc([None, "", "hello", "world"]) == [None, "", "hello", "world"]


@pytest.mark.parametrize(
    ("n", "values", "expected"),
    [
        (2, [None, "", "hello", "world", "extra"], ["hello", "world"]),
        (3, [None, "", 0, False, "hello"], [0, False, "hello"]),
        (1, ["hello", "world"], ["hello"]),
        (3, ["hello"], ["hello"]),
        (2, [None, ""], []),
        (2, [], []),
        (0, ["hello"], []),
    ],
)
def test_take_first_n(n, values, expected):
    assert TakeFirstN(n)(values) == expected


def test_take_first_n_does_not_overconsume():
    values = iter([None, "first", "", "second", "third"])
    assert TakeFirstN(2)(values) == ["first", "second"]
    assert next(values) == "third"
    assert TakeFirstN(0)(values) == []


def test_take_first_n_empty_limit_does_not_iterate():
    def values() -> Iterator[None]:
        pytest.fail("zero limit must not consume values")
        yield

    assert TakeFirstN(0)(values()) == []


def test_take_first_n_invalid_limit():
    with pytest.raises(ValueError, match="non-negative"):
        TakeFirstN(-1)
    with pytest.raises(TypeError):
        TakeFirstN(1.5)  # type: ignore[arg-type]


def test_take_first_n_output_processor():
    loader = ItemLoader()
    loader.default_output_processor = TakeFirstN(2)
    loader.add_value("tags", ["one", "two", "three"])
    assert loader.load_item() == {"tags": ["one", "two"]}


def test_join():
    proc = Join()
    with pytest.raises(TypeError):
        proc([None, "", "hello", "world"])
    assert proc(["", "hello", "world"]) == " hello world"
    assert proc(["hello", "world"]) == "hello world"
    assert isinstance(proc(["hello", "world"]), str)


def test_compose():
    proc = Compose(lambda v: v[0], str.upper)
    assert proc(["hello", "world"]) == "HELLO"
    proc = Compose(str.upper)
    assert proc(None) is None
    proc = Compose(str.upper, stop_on_none=False)
    with pytest.raises(
        ValueError,
        match=r"Error in Compose with .* error='TypeError: (descriptor 'upper'|'str' object expected)",
    ):
        proc(None)
    proc = Compose(str.upper, lambda x: x + 1)
    with pytest.raises(
        ValueError,
        match=r"Error in Compose with .* error='TypeError: (can only|unsupported operand)",
    ):
        proc("hello")


def test_mapcompose():
    def filter_world(x):
        return None if x == "world" else x

    proc = MapCompose(filter_world, str.upper)
    assert proc(["hello", "world", "this", "is", "scrapy"]) == [
        "HELLO",
        "THIS",
        "IS",
        "SCRAPY",
    ]
    proc = MapCompose(filter_world, str.upper)
    assert proc(None) == []
    proc = MapCompose(filter_world, str.upper)
    with pytest.raises(
        ValueError,
        match=r"Error in MapCompose with .* error='TypeError: (descriptor 'upper'|'str' object expected)",
    ):
        proc([1])
    proc = MapCompose(filter_world, lambda x: x + 1)
    with pytest.raises(
        ValueError,
        match=r"Error in MapCompose with .* error='TypeError: (can only|unsupported operand)",
    ):
        proc("hello")


@pytest.mark.parametrize("processor", [Compose, MapCompose])
def test_partial_processor_keeps_context_with_matching_value(processor):
    def prefix_text(prefix, value, loader_context):
        return prefix + value + loader_context["suffix"]

    proc = processor(partial(prefix_text, "loader_context"))
    value = ["text"] if processor is MapCompose else "text"
    expected = (
        ["loader_contexttext!"] if processor is MapCompose else "loader_contexttext!"
    )
    assert proc(value, {"suffix": "!"}) == expected
