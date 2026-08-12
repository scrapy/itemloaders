from collections.abc import Set as AbstractSet

from itemloaders.utils import _MAX_ITERABLE_CLASSES, _iterable_classes, arg_to_iter


def test_arg_to_iter():
    assert hasattr(arg_to_iter(None), "__iter__")
    assert hasattr(arg_to_iter(100), "__iter__")
    assert hasattr(arg_to_iter("lala"), "__iter__")
    assert hasattr(arg_to_iter([1, 2, 3]), "__iter__")
    assert hasattr(arg_to_iter(letter for letter in "abcd"), "__iter__")

    assert list(arg_to_iter(None)) == []
    assert list(arg_to_iter("lala")) == ["lala"]
    assert list(arg_to_iter(100)) == [100]
    assert list(arg_to_iter(letter for letter in "abc")) == ["a", "b", "c"]
    assert list(arg_to_iter([1, 2, 3])) == [1, 2, 3]
    assert list(arg_to_iter({"a": 1})) == [{"a": 1}]

    assert sorted(arg_to_iter({1, 2, 3})) == [1, 2, 3]
    assert sorted(arg_to_iter(frozenset({1, 2, 3}))) == [1, 2, 3]
    assert list(arg_to_iter({"a": 1}.keys())) == ["a"]
    assert list(arg_to_iter(map(str, [1, 2]))) == ["1", "2"]
    assert list(arg_to_iter(iter([1, 2]))) == [1, 2]


def test_arg_to_iter_custom_iterator():
    class Countdown:
        def __init__(self, start: int):
            self.value = start

        def __iter__(self):
            return self

        def __next__(self):
            if not self.value:
                raise StopIteration
            self.value -= 1
            return self.value

    assert list(arg_to_iter(Countdown(2))) == [1, 0]


def test_arg_to_iter_late_registration():
    class Pair:
        def __init__(self, first: int, second: int):
            self._items = (first, second)

        def __iter__(self):
            return iter(self._items)

        def __len__(self):
            return 2

        def __contains__(self, value):
            return value in self._items

    pair = Pair(1, 2)
    assert list(arg_to_iter(pair)) == [pair]

    AbstractSet.register(Pair)
    assert list(arg_to_iter(pair)) == [1, 2]


def test_arg_to_iter_dynamic_classes():
    for index in range(_MAX_ITERABLE_CLASSES + 10):
        obj = type(f"Dynamic{index}", (), {})()
        assert list(arg_to_iter(obj)) == [obj]
    assert len(_iterable_classes) <= _MAX_ITERABLE_CLASSES
