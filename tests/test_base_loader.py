import unittest
from functools import partial

from itemloaders import ItemLoader
from itemloaders.processors import Compose, Identity, Join, MapCompose, TakeFirst


class CustomItemLoader(ItemLoader):
    name_in = MapCompose(lambda v: v.title())


class DefaultedItemLoader(ItemLoader):
    default_input_processor = MapCompose(lambda v: v[:-1])


# test processors
def processor_with_args(value, other=None, loader_context=None):
    if "key" in loader_context:
        return loader_context["key"]
    return value


class BasicItemLoaderTest(unittest.TestCase):
    def test_load_item_using_default_loader(self):
        i = {"summary": "lala"}
        il = ItemLoader(item=i)
        il.add_value("name", "marta")
        item = il.load_item()
        assert item is i
        assert item["summary"] == ["lala"]
        assert item["name"] == ["marta"]

    def test_load_item_using_custom_loader(self):
        il = CustomItemLoader()
        il.add_value("name", "marta")
        item = il.load_item()
        assert item["name"] == ["Marta"]

    def test_load_item_ignore_none_field_values(self):
        def validate_sku(value):
            # Let's assume a SKU is only digits.
            if value.isdigit():
                return value

        class MyLoader(ItemLoader):
            name_out = Compose(lambda vs: vs[0])  # take first which allows empty values
            price_out = Compose(TakeFirst(), float)
            sku_out = Compose(TakeFirst(), validate_sku)

        valid_fragment = "SKU: 1234"
        invalid_fragment = "SKU: not available"
        sku_re = "SKU: (.+)"

        il = MyLoader(item={})
        # Should not return "sku: None".
        il.add_value("sku", [invalid_fragment], re=sku_re)
        # Should not ignore empty values.
        il.add_value("name", "")
        il.add_value("price", ["0"])
        assert il.load_item() == {"name": "", "price": 0.0}

        il.replace_value("sku", [valid_fragment], re=sku_re)
        self.assertEqual(il.load_item()["sku"], "1234")

    def test_self_referencing_loader(self):
        class MyLoader(ItemLoader):
            url_out = TakeFirst()

            def img_url_out(self, values):
                return (self.get_output_value("url") or "") + values[0]

        il = MyLoader(item={})
        il.add_value("url", "http://example.com/")
        il.add_value("img_url", "1234.png")
        assert il.load_item() == {
            "url": "http://example.com/",
            "img_url": "http://example.com/1234.png",
        }

        il = MyLoader(item={})
        il.add_value("img_url", "1234.png")
        assert il.load_item() == {"img_url": "1234.png"}

    def test_add_value(self):
        il = CustomItemLoader()
        il.add_value("name", "marta")
        assert il.get_collected_values("name") == ["Marta"]
        assert il.get_output_value("name") == ["Marta"]

        il.add_value("name", "pepe")
        assert il.get_collected_values("name") == ["Marta", "Pepe"]
        assert il.get_output_value("name") == ["Marta", "Pepe"]

        # test add object value
        il.add_value("summary", {"key": 1})
        assert il.get_collected_values("summary") == [{"key": 1}]

        il.add_value(None, "Jim", lambda x: {"name": x})
        assert il.get_collected_values("name") == ["Marta", "Pepe", "Jim"]

    def test_add_zero(self):
        il = ItemLoader()
        il.add_value("name", 0)
        assert il.get_collected_values("name") == [0]

    def test_add_none(self):
        il = ItemLoader()
        il.add_value("name", None)
        assert il.get_collected_values("name") == []

    def test_replace_value(self):
        il = CustomItemLoader()
        il.replace_value("name", "marta")
        self.assertEqual(il.get_collected_values("name"), ["Marta"])
        self.assertEqual(il.get_output_value("name"), ["Marta"])
        il.replace_value("name", "pepe")
        self.assertEqual(il.get_collected_values("name"), ["Pepe"])
        self.assertEqual(il.get_output_value("name"), ["Pepe"])

        il.replace_value(None, "Jim", lambda x: {"name": x})
        self.assertEqual(il.get_collected_values("name"), ["Jim"])

    def test_replace_value_none(self):
        il = CustomItemLoader()
        il.replace_value("name", None)
        self.assertEqual(il.get_collected_values("name"), [])
        il.replace_value("name", "marta")
        self.assertEqual(il.get_collected_values("name"), ["Marta"])
        il.replace_value(
            "name", None
        )  # when replacing with `None` nothing should happen
        self.assertEqual(il.get_collected_values("name"), ["Marta"])

    def test_get_value(self):
        il = ItemLoader()
        self.assertEqual("FOO", il.get_value(["foo", "bar"], TakeFirst(), str.upper))
        self.assertEqual(
            ["foo", "bar"], il.get_value(["name:foo", "name:bar"], re="name:(.*)$")
        )
        self.assertEqual(
            "foo", il.get_value(["name:foo", "name:bar"], TakeFirst(), re="name:(.*)$")
        )
        self.assertEqual(
            None, il.get_value(["foo", "bar"], TakeFirst(), re="name:(.*)$")
        )
        self.assertEqual(None, il.get_value(None, TakeFirst()))

        il.add_value("name", ["name:foo", "name:bar"], TakeFirst(), re="name:(.*)$")
        self.assertEqual(["foo"], il.get_collected_values("name"))
        il.replace_value("name", "name:bar", re="name:(.*)$")
        self.assertEqual(["bar"], il.get_collected_values("name"))

    def test_iter_on_input_processor_input(self):
        class NameFirstItemLoader(ItemLoader):
            name_in = TakeFirst()

        il = NameFirstItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_collected_values("name"), ["marta"])
        il = NameFirstItemLoader()
        il.add_value("name", ["marta", "jose"])
        self.assertEqual(il.get_collected_values("name"), ["marta"])

        il = NameFirstItemLoader()
        il.replace_value("name", "marta")
        self.assertEqual(il.get_collected_values("name"), ["marta"])
        il = NameFirstItemLoader()
        il.replace_value("name", ["marta", "jose"])
        self.assertEqual(il.get_collected_values("name"), ["marta"])

        il = NameFirstItemLoader()
        il.add_value("name", "marta")
        il.add_value("name", ["jose", "pedro"])
        self.assertEqual(il.get_collected_values("name"), ["marta", "jose"])

    def test_map_compose_filter(self):
        def filter_world(x):
            return None if x == "world" else x

        proc = MapCompose(filter_world, str.upper)
        self.assertEqual(
            proc(["hello", "world", "this", "is", "scrapy"]),
            ["HELLO", "THIS", "IS", "SCRAPY"],
        )

    def test_map_compose_filter_multil(self):
        class CustomItemLoader(ItemLoader):
            name_in = MapCompose(lambda v: v.title(), lambda v: v[:-1])

        il = CustomItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["Mart"])
        item = il.load_item()
        self.assertEqual(item["name"], ["Mart"])

    def test_default_input_processor(self):
        il = DefaultedItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["mart"])

    def test_inherited_default_input_processor(self):
        class InheritDefaultedItemLoader(DefaultedItemLoader):
            pass

        il = InheritDefaultedItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["mart"])

    def test_input_processor_inheritance(self):
        class ChildItemLoader(CustomItemLoader):
            url_in = MapCompose(lambda v: v.lower())

        il = ChildItemLoader()
        il.add_value("url", "HTTP://scrapy.ORG")
        self.assertEqual(il.get_output_value("url"), ["http://scrapy.org"])
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["Marta"])

        class ChildChildItemLoader(ChildItemLoader):
            url_in = MapCompose(lambda v: v.upper())
            summary_in = MapCompose(lambda v: v)

        il = ChildChildItemLoader()
        il.add_value("url", "http://scrapy.org")
        self.assertEqual(il.get_output_value("url"), ["HTTP://SCRAPY.ORG"])
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["Marta"])

    def test_empty_map_compose(self):
        class IdentityDefaultedItemLoader(DefaultedItemLoader):
            name_in = MapCompose()

        il = IdentityDefaultedItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["marta"])

    def test_identity_input_processor(self):
        class IdentityDefaultedItemLoader(DefaultedItemLoader):
            name_in = Identity()

        il = IdentityDefaultedItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["marta"])

    def test_extend_custom_input_processors(self):
        class ChildItemLoader(CustomItemLoader):
            name_in = MapCompose(CustomItemLoader.name_in, str.swapcase)

        il = ChildItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["mARTA"])

    def test_extend_default_input_processors(self):
        class ChildDefaultedItemLoader(DefaultedItemLoader):
            name_in = MapCompose(
                DefaultedItemLoader.default_input_processor, str.swapcase
            )

        il = ChildDefaultedItemLoader()
        il.add_value("name", "marta")
        self.assertEqual(il.get_output_value("name"), ["MART"])

    def test_output_processor_using_function(self):
        il = CustomItemLoader()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), ["Mar", "Ta"])

        class TakeFirstItemLoader(CustomItemLoader):
            name_out = " ".join

        il = TakeFirstItemLoader()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), "Mar Ta")

    def test_output_processor_error(self):
        class CustomItemLoader(ItemLoader):
            name_out = MapCompose(float)

        il = CustomItemLoader()
        il.add_value("name", ["$10"])
        try:
            float("$10")
        except Exception as e:
            expected_exc_str = str(e)

        exc = None
        try:
            il.load_item()
        except Exception as e:
            exc = e
        assert isinstance(exc, ValueError)
        s = str(exc)
        assert "name" in s, s
        assert "$10" in s, s
        assert "ValueError" in s, s
        assert expected_exc_str in s, s

    def test_output_processor_using_classes(self):
        il = CustomItemLoader()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), ["Mar", "Ta"])

        class TakeFirstItemLoader1(CustomItemLoader):
            name_out = Join()

        il = TakeFirstItemLoader1()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), "Mar Ta")

        class TakeFirstItemLoader2(CustomItemLoader):
            name_out = Join("<br>")

        il = TakeFirstItemLoader2()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), "Mar<br>Ta")

    def test_default_output_processor(self):
        il = CustomItemLoader()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), ["Mar", "Ta"])

        class LalaItemLoader(CustomItemLoader):
            default_output_processor = Identity()

        il = LalaItemLoader()
        il.add_value("name", ["mar", "ta"])
        self.assertEqual(il.get_output_value("name"), ["Mar", "Ta"])

    def test_loader_context_on_declaration(self):
        class ChildItemLoader(CustomItemLoader):
            url_in = MapCompose(processor_with_args, key="val")

        il = ChildItemLoader()
        il.add_value("url", "text")
        self.assertEqual(il.get_output_value("url"), ["val"])
        il.replace_value("url", "text2")
        self.assertEqual(il.get_output_value("url"), ["val"])

    def test_loader_context_on_instantiation(self):
        class ChildItemLoader(CustomItemLoader):
            url_in = MapCompose(processor_with_args)

        il = ChildItemLoader(key="val")
        il.add_value("url", "text")
        self.assertEqual(il.get_output_value("url"), ["val"])
        il.replace_value("url", "text2")
        self.assertEqual(il.get_output_value("url"), ["val"])

    def test_loader_context_on_assign(self):
        class ChildItemLoader(CustomItemLoader):
            url_in = MapCompose(processor_with_args)

        il = ChildItemLoader()
        il.context["key"] = "val"
        il.add_value("url", "text")
        self.assertEqual(il.get_output_value("url"), ["val"])
        il.replace_value("url", "text2")
        self.assertEqual(il.get_output_value("url"), ["val"])

    def test_item_passed_to_input_processor_functions(self):
        def processor(value, loader_context):
            return loader_context["item"]["name"]

        class ChildItemLoader(CustomItemLoader):
            url_in = MapCompose(processor)

        it = {"name": "marta"}
        il = ChildItemLoader(item=it)
        il.add_value("url", "text")
        self.assertEqual(il.get_output_value("url"), ["marta"])
        il.replace_value("url", "text2")
        self.assertEqual(il.get_output_value("url"), ["marta"])

    # def test_add_value_on_unknown_field(self):
    #     il = CustomItemLoader()
    #     self.assertRaises(KeyError, il.add_value, 'wrong_field', ['lala', 'lolo'])

    def test_compose_processor(self):
        class CustomItemLoader(ItemLoader):
            name_out = Compose(lambda v: v[0], lambda v: v.title(), lambda v: v[:-1])

        il = CustomItemLoader()
        il.add_value("name", ["marta", "other"])
        self.assertEqual(il.get_output_value("name"), "Mart")
        item = il.load_item()
        self.assertEqual(item["name"], "Mart")

    def test_partial_processor(self):
        def join(values, sep=None, loader_context=None, ignored=None):
            if sep is not None:
                return sep.join(values)
            elif loader_context and "sep" in loader_context:
                return loader_context["sep"].join(values)
            else:
                return "".join(values)

        class CustomItemLoader(ItemLoader):
            name_out = Compose(partial(join, sep="+"))
            url_out = Compose(partial(join, loader_context={"sep": "."}))
            summary_out = Compose(partial(join, ignored="foo"))

        il = CustomItemLoader()
        il.add_value("name", ["rabbit", "hole"])
        il.add_value("url", ["rabbit", "hole"])
        il.add_value("summary", ["rabbit", "hole"])
        item = il.load_item()
        self.assertEqual(item["name"], "rabbit+hole")
        self.assertEqual(item["url"], "rabbit.hole")
        self.assertEqual(item["summary"], "rabbithole")

    def test_error_input_processor(self):
        class CustomItemLoader(ItemLoader):
            name_in = MapCompose(float)

        il = CustomItemLoader()
        self.assertRaises(ValueError, il.add_value, "name", ["marta", "other"])

    def test_error_output_processor(self):
        class CustomItemLoader(ItemLoader):
            name_out = Compose(Join(), float)

        il = CustomItemLoader()
        il.add_value("name", "marta")
        with self.assertRaises(ValueError):
            il.load_item()

    def test_error_processor_as_argument(self):
        il = CustomItemLoader()
        self.assertRaises(
            ValueError, il.add_value, "name", ["marta", "other"], Compose(float)
        )

    def test_get_unset_value(self):
        loader = ItemLoader()
        self.assertEqual(loader.load_item(), {})
        self.assertEqual(loader.get_output_value("foo"), [])
        self.assertEqual(loader.load_item(), {})


class BaseNoInputReprocessingLoader(ItemLoader):
    title_in = MapCompose(str.upper)
    title_out = TakeFirst()


class NoInputReprocessingDictLoader(BaseNoInputReprocessingLoader):
    default_item_class = dict


class NoInputReprocessingFromDictTest(unittest.TestCase):
    """
    Loaders initialized from loaded items must not reprocess fields (dict instances)
    """

    def test_avoid_reprocessing_with_initial_values_single(self):
        il = NoInputReprocessingDictLoader(item={"title": "foo"})
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {"title": "foo"})
        self.assertEqual(
            NoInputReprocessingDictLoader(item=il_loaded).load_item(), {"title": "foo"}
        )

    def test_avoid_reprocessing_with_initial_values_list(self):
        il = NoInputReprocessingDictLoader(item={"title": ["foo", "bar"]})
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {"title": "foo"})
        self.assertEqual(
            NoInputReprocessingDictLoader(item=il_loaded).load_item(), {"title": "foo"}
        )

    def test_avoid_reprocessing_without_initial_values_single(self):
        il = NoInputReprocessingDictLoader()
        il.add_value("title", "foo")
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {"title": "FOO"})
        self.assertEqual(
            NoInputReprocessingDictLoader(item=il_loaded).load_item(), {"title": "FOO"}
        )

    def test_avoid_reprocessing_without_initial_values_list(self):
        il = NoInputReprocessingDictLoader()
        il.add_value("title", ["foo", "bar"])
        il_loaded = il.load_item()
        self.assertEqual(il_loaded, {"title": "FOO"})
        self.assertEqual(
            NoInputReprocessingDictLoader(item=il_loaded).load_item(), {"title": "FOO"}
        )
