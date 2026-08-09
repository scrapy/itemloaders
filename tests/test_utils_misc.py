from itemloaders.utils import arg_to_iter


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
