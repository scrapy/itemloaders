from itemloaders.processors import SelectJmes

test_list_equals = {
    "simple": ("foo.bar", {"foo": {"bar": "baz"}}, "baz"),
    "invalid": ("foo.bar.baz", {"foo": {"bar": "baz"}}, None),
    "top_level": ("foo", {"foo": {"bar": "baz"}}, {"bar": "baz"}),
    "double_vs_single_quote_string": ("foo.bar", {"foo": {"bar": "baz"}}, "baz"),
    "dict": (
        "foo.bar[*].name",
        {"foo": {"bar": [{"name": "one"}, {"name": "two"}]}},
        ["one", "two"],
    ),
    "list": ("[1]", [1, 2], 2),
}


def test_output():
    for key, value in test_list_equals.items():
        expr, test_list, expected = value
        test = SelectJmes(expr)(test_list)
        assert test == expected, f"test {key!r} got {test} expected {expected}"
