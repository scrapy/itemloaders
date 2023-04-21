import unittest

from itemloaders.processors import Compose, Identity, Join, MapCompose, TakeFirst


class ProcessorsTest(unittest.TestCase):
    def test_take_first(self):
        proc = TakeFirst()
        self.assertEqual(proc([None, "", "hello", "world"]), "hello")
        self.assertEqual(proc([None, "", 0, "hello", "world"]), 0)

    def test_identity(self):
        proc = Identity()
        self.assertEqual(
            proc([None, "", "hello", "world"]), [None, "", "hello", "world"]
        )

    def test_join(self):
        proc = Join()
        self.assertRaises(TypeError, proc, [None, "", "hello", "world"])
        self.assertEqual(proc(["", "hello", "world"]), " hello world")
        self.assertEqual(proc(["hello", "world"]), "hello world")
        self.assertIsInstance(proc(["hello", "world"]), str)

    def test_compose(self):
        proc = Compose(lambda v: v[0], str.upper)
        self.assertEqual(proc(["hello", "world"]), "HELLO")
        proc = Compose(str.upper)
        self.assertEqual(proc(None), None)
        proc = Compose(str.upper, stop_on_none=False)
        self.assertRaises(ValueError, proc, None)
        proc = Compose(str.upper, lambda x: x + 1)
        self.assertRaises(ValueError, proc, "hello")

    def test_mapcompose(self):
        def filter_world(x):
            return None if x == "world" else x

        proc = MapCompose(filter_world, str.upper)
        self.assertEqual(
            proc(["hello", "world", "this", "is", "scrapy"]),
            ["HELLO", "THIS", "IS", "SCRAPY"],
        )
        proc = MapCompose(filter_world, str.upper)
        self.assertEqual(proc(None), [])
        proc = MapCompose(filter_world, str.upper)
        self.assertRaises(ValueError, proc, [1])
        proc = MapCompose(filter_world, lambda x: x + 1)
        self.assertRaises(ValueError, proc, "hello")
