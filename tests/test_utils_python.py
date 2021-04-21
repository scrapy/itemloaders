import functools
import operator
import platform
import unittest
from datetime import datetime

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
            def __init__(self, a, b, c):
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

        self.assertEqual(get_func_args(f1), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(f2), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(f3), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(A), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(a.method), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(partial_f1), ['b', 'c'])
        self.assertEqual(get_func_args(partial_f2), ['a', 'c'])
        self.assertEqual(get_func_args(partial_f3), ['c'])
        self.assertEqual(get_func_args(cal), ['a', 'b', 'c'])
        self.assertEqual(get_func_args(object), [])

        if platform.python_implementation() == 'CPython':
            # TODO: how do we fix this to return the actual argument names?
            self.assertEqual(get_func_args(str.split), [])
            self.assertEqual(get_func_args(" ".join), [])
            self.assertEqual(get_func_args(operator.itemgetter(2)), [])
        elif platform.python_implementation() == 'PyPy':
            self.assertEqual(get_func_args(str.split, stripself=True), ['sep', 'maxsplit'])
            self.assertEqual(get_func_args(operator.itemgetter(2), stripself=True), ['obj'])

            build_date = datetime.strptime(platform.python_build()[1], '%b %d %Y')
            if build_date >= datetime(2020, 4, 7):  # PyPy 3.6-v7.3.1
                self.assertEqual(get_func_args(" ".join, stripself=True), ['iterable'])
            else:
                self.assertEqual(get_func_args(" ".join, stripself=True), ['list'])


if __name__ == "__main__":
    unittest.main()
