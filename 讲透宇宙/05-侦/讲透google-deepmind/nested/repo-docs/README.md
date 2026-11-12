# Nested

A Python library for easy access and manipulation of nested data structures.

`nested` treats Python objects as trees: containers (`dict`, `list`, `tuple`,
`namedtuple`, `dataclass`, `attrs`) form the nodes and everything else forms
the leaves. It provides a concise, dot-separated field-path syntax
(e.g. `'a.1.bar'`) for accessing, checking, updating, adding, removing,
and comparing elements at arbitrary depth — without writing chains of
brackets and attribute lookups by hand.

## Installation

```bash
pip install gdm-nested
```

## Quick Start

```python
import collections
import nested

MyTuple = collections.namedtuple('MyTuple', ['foo', 'bar'])
obj = {
    'a': [1, (2, 3, 4)],
    'b': MyTuple(foo='f', bar='b'),
}

# Access deeply nested values with a dot-separated path.
nested.access_field(obj, 'a.0')      # → 1
nested.access_field(obj, 'a.1.2')    # → 4
nested.access_field(obj, 'b.bar')    # → 'b'

# Check if a path exists.
nested.check_field(obj, 'a.0')       # → True
nested.check_field(obj, 'a.99')      # → False

# Update (or upsert) a value.
nested.update_field(obj, 'b.foo', 'g')
# → {'a': [1, (2, 3, 4)], 'b': MyTuple(foo='g', bar='b')}

# Remove a field and get the popped value.
obj2, popped = nested.remove_field(obj, 'b')
# obj2   → {'a': [1, (2, 3, 4)]}
# popped → MyTuple(foo='f', bar='b')
```

## Supported Container Types

`nested` recognises the following types as tree **nodes**:

| Type | Description |
|---|---|
| `dict` | Any `dict` subclass, `collections.OrderedDict`, `collections.defaultdict`, `ml_collections.ConfigDict` |
| `list` | Any `list` instance |
| `tuple` | Plain tuples (not namedtuples) |
| `namedtuple` | Any tuple-like class with a `_fields` attribute |
| `dataclass` | Any `dataclasses.dataclass` instance |
| `attrs` | Any `attr.s` / `attrs.define` instance |

Everything else is treated as an opaque **leaf**.

> **Note:** Sequences and custom containers are only recognised as structures
> when derived from `dict` or `list`.

## Field Path Syntax

Fields are specified as dot-separated strings, tuples, or single keys:

```python
# All of these are equivalent:
nested.access_field(obj, 'a.1.2')
nested.access_field(obj, ('a', 1, 2))
nested.access_field(obj, ('a', '1', '2'))
```

- **String keys** address dict keys and namedtuple/dataclass/attrs field names.
- **Integer keys** address list and tuple indices (including negative indices).

## Comparison with `dm-tree`

At first glance, `nested` might seem similar to
[google-deepmind/tree](https://github.com/google-deepmind/tree), as both operate
on nested Python structures (dictionaries, lists, tuples). However, they solve
entirely different problems and are highly complementary.

* **`tree` is for Transformation:** It focuses on applying operations across the
entirety of a nested structure. You use `tree` when you want to map a function
over every leaf node (`tree.map_structure`), flatten a complex structure into a
1D list (`tree.flatten`), or verify that two structures have the same exact
shape.
* **`nested` is for Navigation and Access:** It focuses on traversal and
targeting. `tree` lacks utilities to easily grab a specific value deep inside a
structure without manual indexing. `nested` provides the tools to safely and
cleanly query, extract, and navigate to specific paths within complex,
heavily-nested objects.

**Rule of thumb:**
If you need to multiply every number in a nested dictionary by 2, use `tree`.
If you need to safely extract a specific configuration value buried five levels
deep in that dictionary, use `nested`.

## API Reference

### Accessing Fields

#### `access_field(nested_obj, field)`

Returns the value at the given field path.

```python
nested.access_field({'x': [10, 20]}, 'x.1')  # → 20
```

#### `access_fields(nested_obj, fields)`

Returns a list of values for multiple field paths.

```python
nested.access_fields({'x': 1, 'y': 2}, ['x', 'y'])  # → [1, 2]
```

#### `get(nested_obj, field, value=None)`

Like `access_field`, but returns a default value instead of raising when the
field does not exist.

```python
nested.get({'x': 1}, 'y', 'default')  # → 'default'
```

---

### Checking Fields

#### `check_field(nested_obj, field)`

Returns `True` if the field path exists.

```python
nested.check_field({'x': [1]}, 'x.0')  # → True
nested.check_field({'x': [1]}, 'x.5')  # → False
```

#### `check_fields(nested_obj, fields)`

Returns a list of booleans for multiple field paths.

```python
all(nested.check_fields(obj, ['a', 'b']))  # True if both exist
```

---

### Updating Fields

#### `update_field(nested_obj, field, value)`

Replaces the value if the field exists, or inserts it if it doesn't (upsert).

```python
nested.update_field({'x': 1}, 'x', 2)  # → {'x': 2}
nested.update_field({'x': 1}, 'y', 2)  # → {'x': 1, 'y': 2}
```

#### `update_fields(nested_obj, *field_value_tuples, **field_value_kwargs)`

Batch update/upsert multiple fields at once.

```python
nested.update_fields({'a': 1}, ('b', 2), c=3)  # → {'a': 1, 'b': 2, 'c': 3}
```

---

### Replacing Fields

#### `replace_field(nested_obj, field, value)`

Like `update_field`, but **raises `KeyError`** if the field does not already
exist.

```python
nested.replace_field({'x': 1}, 'x', 2)  # → {'x': 2}

nested.replace_field({'x': 1}, 'y', 2)
# raises KeyError: '"y" field not in structure.'

nested.replace_field({'x': {'z': 1}}, 'x.y', 2)
# raises KeyError: '"y" field not in structure.'
```

#### `replace_fields(nested_obj, *field_value_tuples, **field_value_kwargs)`

Batch version of `replace_field`.

---

### Adding Fields

#### `add_field(nested_obj, field, value)`

Like `update_field`, but **raises `KeyError`** if the field already exists.

```python
nested.add_field({'x': 1}, 'y', 2)  # → {'x': 1, 'y': 2}

# raises KeyError: '"x" field already in structure.'
nested.add_field({'x': 1}, 'x', 2)
```

#### `add_fields(nested_obj, *field_value_tuples, **field_value_kwargs)`

Batch version of `add_field`.

> **Note:** For sequences, elements are *inserted* at the given index. Order
> matters — additions are applied sequentially.

---

### Removing Fields

#### `remove_field(nested_obj, field, *, default=...)`

Removes a field and returns a `(modified_obj, popped_value)` tuple. Pass
`default` to suppress errors when the field is missing.

```python
obj, val = nested.remove_field({'x': 1, 'y': 2}, 'x')  # obj → {'y': 2}, val → 1

obj, val = nested.remove_field({'x': 1, 'y': 2}, 'z', default=3)
# obj → {'y': 2}, val → 3
```

#### `remove_fields(nested_obj, *fields, default=...)`

Removes multiple fields sequentially, returning a
`(modified_obj, [popped_values])` tuple.

> **Note:** Removals are applied sequentially, so indices may shift for
> list-based structures.

---

### Introspection

#### `field_names(nested_obj, root='')`

Returns a structure parallel to `nested_obj` where each leaf is replaced by
its dot-separated path string.

```python
nested.field_names({'a': [1, 2], 'b': 3})  # → {'a': ['a.0', 'a.1'], 'b': 'b'}
```

---

### Comparison

#### `assert_equal(a, b, custom_is_equals=...)`

Raises `ValueError` if two nested structures are not structurally and
value-equal. NumPy arrays are compared element-wise by default. Custom
comparators can be supplied via `custom_is_equals`.

```python
nested.assert_equal({'x': [1, 2]}, {'x': [1, 2]})  # passes

nested.assert_equal({'x': {'y':1}}, {'x': {'y':2}})
# ValueError: The two nested structure are not equal at path: "x.y".

nested.assert_equal({'x': {'y':1}}, {'x': {'z':2}})
# ValueError: The two structures don't have the same nested structure.
# First structure: type=dict str={'x': {'y': None}}
# Second structure: type=dict str={'x': {'z': None}}
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## Licence and Disclaimer

Copyright 2026 Google LLC

All software is licensed under the Apache License, Version 2.0 (Apache 2.0); you
may not use this file except in compliance with the Apache 2.0 license. You may
obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 are distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the licenses for the specific language governing permissions and limitations
under those licenses.

This is not an official Google product.
