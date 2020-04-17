"""
Item Loader

See documentation in docs/topics/loaders.rst
"""
from collections import defaultdict
from contextlib import suppress

from itemloaders.common import wrap_loader_context
from itemloaders.processors import Identity
from itemloaders.utils import arg_to_iter, extract_regex, flatten


def unbound_method(method):
    """
    Allow to use single-argument functions as input or output processors
    (no need to define an unused first 'self' argument)
    """
    with suppress(AttributeError):
        if '.' not in method.__qualname__:
            return method.__func__
    return method


class ItemLoader:

    default_item_class = dict
    default_input_processor = Identity()
    default_output_processor = Identity()

    def __init__(self, item=None, parent=None, **context):
        if item is None:
            item = self.default_item_class()
        self.context = context
        self.parent = parent
        self._local_item = context['item'] = item
        self._local_values = defaultdict(list)
        # values from initial item
        for field_name, value in item.items():
            self._values[field_name] += arg_to_iter(value)

    @property
    def _values(self):
        if self.parent is not None:
            return self.parent._values
        else:
            return self._local_values

    @property
    def item(self):
        if self.parent is not None:
            return self.parent.item
        else:
            return self._local_item

    def add_value(self, field_name, value, *processors, **kw):
        value = self.get_value(value, *processors, **kw)
        if value is None:
            return
        if not field_name:
            for k, v in value.items():
                self._add_value(k, v)
        else:
            self._add_value(field_name, value)

    def replace_value(self, field_name, value, *processors, **kw):
        value = self.get_value(value, *processors, **kw)
        if value is None:
            return
        if not field_name:
            for k, v in value.items():
                self._replace_value(k, v)
        else:
            self._replace_value(field_name, value)

    def _add_value(self, field_name, value):
        value = arg_to_iter(value)
        processed_value = self._process_input_value(field_name, value)
        if processed_value:
            self._values[field_name] += arg_to_iter(processed_value)

    def _replace_value(self, field_name, value):
        self._values.pop(field_name, None)
        self._add_value(field_name, value)

    def get_value(self, value, *processors, **kw):
        regex = kw.get('re', None)
        if regex:
            value = arg_to_iter(value)
            value = flatten(extract_regex(regex, x) for x in value)

        for proc in processors:
            if value is None:
                break
            _proc = proc
            proc = wrap_loader_context(proc, self.context)
            try:
                value = proc(value)
            except Exception as e:
                raise ValueError("Error with processor %s value=%r error='%s: %s'" %
                                 (_proc.__class__.__name__, value,
                                  type(e).__name__, str(e)))
        return value

    def load_item(self):
        item = self.item
        for field_name in tuple(self._values):
            value = self.get_output_value(field_name)
            if value is not None:
                print(type(value))
                item[field_name] = value

        return item

    def get_output_value(self, field_name):
        proc = self.get_output_processor(field_name)
        proc = wrap_loader_context(proc, self.context)
        try:
            return proc(self._values[field_name])
        except Exception as e:
            raise ValueError("Error with output processor: field=%r value=%r error='%s: %s'" %
                             (field_name, self._values[field_name], type(e).__name__, str(e)))

    def get_collected_values(self, field_name):
        return self._values[field_name]

    def get_input_processor(self, field_name):
        proc = getattr(self, '%s_in' % field_name, None)
        if not proc:
            proc = self._get_item_field_attr(field_name, 'input_processor',
                                             self.default_input_processor)
        return unbound_method(proc)

    def get_output_processor(self, field_name):
        proc = getattr(self, '%s_out' % field_name, None)
        if not proc:
            proc = self._get_item_field_attr(field_name, 'output_processor',
                                             self.default_output_processor)
        return unbound_method(proc)

    def _process_input_value(self, field_name, value):
        proc = self.get_input_processor(field_name)
        _proc = proc
        proc = wrap_loader_context(proc, self.context)
        try:
            return proc(value)
        except Exception as e:
            raise ValueError(
                "Error with input processor %s: field=%r value=%r "
                "error='%s: %s'" % (_proc.__class__.__name__, field_name,
                                    value, type(e).__name__, str(e)))

    def _get_item_field_attr(self, field_name, key, default=None):
        # if isinstance(self.item, Item):
        #     value = self.item.fields[field_name].get(key, default)
        # else:
        #     value = default
        # return value
        return default
