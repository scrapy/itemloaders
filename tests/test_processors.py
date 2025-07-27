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
    with pytest.raises(ValueError, match="doesn't apply to a 'NoneType' object"):
        proc(None)
    proc = Compose(str.upper, lambda x: x + 1)
    with pytest.raises(ValueError, match="can only concatenate str"):
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
    with pytest.raises(ValueError, match="doesn't apply to a 'int' object"):
        proc([1])
    proc = MapCompose(filter_world, lambda x: x + 1)
    with pytest.raises(ValueError, match="can only concatenate str"):
        proc("hello")
