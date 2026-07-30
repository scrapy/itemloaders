import pytest

from itemloaders.processors import Compose, Identity, Join, MapCompose, TakeFirst


def test_take_first():
    proc = TakeFirst()
    assert proc([None, "", "hello", "world"]) == "hello"
    assert proc([None, "", 0, "hello", "world"]) == 0


def test_identity():
    proc = Identity()
    assert proc([None, "", "hello", "world"]) == [None, "", "hello", "world"]


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


def test_add_value_preserves_zero():
    """Integer 0 must not be dropped as empty (issue #73)."""
    from itemloaders import ItemLoader
    from itemloaders.processors import Identity, TakeFirst

    loader = ItemLoader(item={})
    loader.default_input_processor = Identity()
    loader.default_output_processor = TakeFirst()
    loader.add_value("count", 0)
    assert loader.get_output_value("count") == 0
    item = loader.load_item()
    assert item["count"] == 0
