import unittest

from itemloaders.utils import arg_to_iter


class UtilsMiscTestCase(unittest.TestCase):
    def test_arg_to_iter(self):
        assert hasattr(arg_to_iter(None), "__iter__")
        assert hasattr(arg_to_iter(100), "__iter__")
        assert hasattr(arg_to_iter("lala"), "__iter__")
        assert hasattr(arg_to_iter([1, 2, 3]), "__iter__")
        assert hasattr(arg_to_iter(letter for letter in "abcd"), "__iter__")

        self.assertEqual(list(arg_to_iter(None)), [])
        self.assertEqual(list(arg_to_iter("lala")), ["lala"])
        self.assertEqual(list(arg_to_iter(100)), [100])
        self.assertEqual(list(arg_to_iter(letter for letter in "abc")), ["a", "b", "c"])
        self.assertEqual(list(arg_to_iter([1, 2, 3])), [1, 2, 3])
        self.assertEqual(list(arg_to_iter({"a": 1})), [{"a": 1}])


if __name__ == "__main__":
    unittest.main()
