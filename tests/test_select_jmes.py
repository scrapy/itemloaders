import unittest

from itemloaders.processors import SelectJmes


class SelectJmesTestCase(unittest.TestCase):
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

    def test_output(self):
        for key in self.test_list_equals:
            expr, test_list, expected = self.test_list_equals[key]
            test = SelectJmes(expr)(test_list)
            self.assertEqual(
                test, expected, msg=f"test {key!r} got {test} expected {expected}"
            )
