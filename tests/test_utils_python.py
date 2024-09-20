import functools
import operator
import platform
import sys
import unittest
from typing import Any

from itemloaders.utils import get_func_args


class UtilsPythonTestCase(unittest.TestCase):
    def test_get_func_args(self):
        def f1(a, b, c):
            pass

        def f2(a, b=None, c=None):
            pass

        def f3(a, b=None, *, c=None):
            pass

        class A:
            def __init__(self, a: Any, b: Any, c: Any):
                pass

            def method(self, a, b, c):
                pass

        class Callable:
            def __call__(self, a, b, c):
                pass

        a = A(1, 2, 3)
        cal = Callable()
        partial_f1 = functools.partial(f1, None)
        partial_f2 = functools.partial(f1, b=None)
        partial_f3 = functools.partial(partial_f2, None)

        self.assertEqual(get_func_args(f1), ["a", "b", "c"])
        self.assertEqual(get_func_args(f2), ["a", "b", "c"])
        self.assertEqual(get_func_args(f3), ["a", "b", "c"])
        self.assertEqual(get_func_args(A), ["a", "b", "c"])
        self.assertEqual(get_func_args(a.method), ["a", "b", "c"])
        self.assertEqual(get_func_args(partial_f1), ["b", "c"])
        self.assertEqual(get_func_args(partial_f2), ["a", "c"])
        self.assertEqual(get_func_args(partial_f3), ["c"])
        self.assertEqual(get_func_args(cal), ["a", "b", "c"])
        self.assertEqual(get_func_args(object), [])
        self.assertEqual(get_func_args(str.split, stripself=True), ["sep", "maxsplit"])
        self.assertEqual(get_func_args(" ".join, stripself=True), ["iterable"])

        if sys.version_info >= (3, 13) or platform.python_implementation() == "PyPy":
            # the correct and correctly extracted signature
            self.assertEqual(
                get_func_args(operator.itemgetter(2), stripself=True), ["obj"]
            )
        elif platform.python_implementation() == "CPython":
            # ["args", "kwargs"] is a correct result for the pre-3.13 incorrect function signature
            # [] is an incorrect result on even older CPython (https://github.com/python/cpython/issues/86951)
            self.assertIn(
                get_func_args(operator.itemgetter(2), stripself=True),
                [[], ["args", "kwargs"]],
            )


if __name__ == "__main__":
    unittest.main()
