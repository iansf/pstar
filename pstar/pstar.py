# -*- coding: utf-8 -*-
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""`pstar` class implementations.

Import like this:
```python
from pstar import *
```
or like this:
```python
from pstar import defaultpdict, pdict, plist, pset
```
"""

import collections
from collections import defaultdict
import inspect
from multiprocessing.dummy import Pool
import operator
import sys
import types

try:
  import matplotlib.pyplot as plt
except ImportError:
  plt = None

try:
  import numpy as np
except ImportError:
  np = None

try:
  import pandas as pd
except ImportError:
  pd = None

from qj import qj


# pylint: disable=line-too-long,invalid-name,g-explicit-length-test,broad-except,g-long-lambda


def compatible_metaclass(meta, *bases):
  class metaclass(meta):
    __call__ = type.__call__
    __init__ = type.__init__

    def __new__(cls, name, this_bases, d):
      if this_bases is None:
        return type.__new__(cls, name, (), d)
      return meta(name, bases, d)
  return metaclass('_temporary_class', None, {})


KeyValue = collections.namedtuple('KeyValue', 'key value')


################################################################################
################################################################################
################################################################################
# pdict class
################################################################################
################################################################################
################################################################################
class pdict(dict):
  """`dict` subclass where everything is automatically a property.

  Examples:

  Use with dot notation or subscript notation:
  ```python
    p = pdict()
    p.foo = 1
    assert (p['foo'] == p.foo == 1)
  ```

  `list` subscripts also work and return a `plist` of the corresponding keys:
  ```python
    p = pdict(foo=1, bar=2)
    assert (p[['foo', 'bar']].aslist() == [1, 2])
  ```

  Setting with a `list` subscript also works, using a single element or a matching
  `list` for the values:
  ```python
    p = pdict()
    p[['foo', 'bar']] = 1
    assert (p[['foo', 'bar']].aslist() == [1, 1])
    p[['foo', 'bar']] = [1, 2]
    assert (p[['foo', 'bar']].aslist() == [1, 2])
  ```

  `pdict.update()` returns `self`, rather than `None`, to support chaining:
  ```python
    p = pdict(foo=1, bar=2)
    p.update(bar=3).baz = 4
    assert (p.bar == 3)
    assert ('baz' in p.keys())
  ```
  """

  def __init__(self, *a, **kw):
    """Initialize `pdict`.

    Examples:
    ```python
    pd1 = pdict(foo=1, bar=2.0, baz='three')
    pd2 = pdict({'foo': 1, 'bar': 2.0, 'baz': 'three'})
    assert (pd1 == pd2)
    ```

    Args:
      *a: Positional arguments passed through to `dict()`.
      **kw: Keyword arguments passed through to `dict()`.

    Returns:
      `None`. `pdict` is initialized.
    """
    dict.__init__(self, *a, **kw)
    self.__dict__ = self

  def __getitem__(self, key):
    """Subscript operation. Keys can be any normal `dict` keys or `list`s of such keys.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    assert (pd['foo'] == pd.foo == 1)
    assert (pd[['foo', 'bar', 'baz']].aslist() == [1, 2.0, 'three'])
    ```

    When indexing with a `list`, the returned `plist` is rooted at a `plist` of
    `KeyValue` `tuple`s, making it easy to recover the keys that gave the values, and
    allows the `plist` to be turned back into a corresponding `pdict`:
    ```python
    assert (pd[['foo', 'baz']].root().aslist() ==
            [('foo', 1), ('baz', 'three')])
    assert (pd[['foo', 'baz']].pdict() ==
            dict(foo=1, baz='three'))
    ```

    Args:
      key: Any `hash`able object, or a `list` of `hash`able objects.

    Returns:
      Either the value held at `key`, or a `plist` of values held at each key in the `list`
      of keys, when called with a `list` of keys.
    """
    if isinstance(key, list):
      return plist([self[k] for k in key], root=plist([KeyValue(k, self[k]) for k in key]))
    else:
      return dict.__getitem__(self, key)

  def __setitem__(self, key, value):
    """Subscript assignment operation. Keys and values can be scalars or `list`s.

    Examples:

    `pdict` assignment works normally for any `hash`able `key`:
    ```python
    pd = pdict()
    pd['foo'] = 1
    assert (pd.foo == pd['foo'] == 1)
    ```

    `pdict` assignment can also work with a `list` of `hash`able `key`s:
    ```python
    pd[['bar', 'baz']] = plist[2.0, 'three']
    assert (pd.bar == pd['bar'] == 2.0)
    assert (pd.baz == pd['baz'] == 'three')
    ```

    Args:
      key: Any `hash`able object, or a `list` of `hash`able objects.
      value: Any value, or a `plist` of values that matches the shape of `key`, if it
             is a `list`.

    Returns:
      `self`, to allow chaining with direct calls to `pdict.__setitem__`.
    """
    if isinstance(key, list):
      value = _ensure_len(len(key), value)
      for k, v in zip(key, value):
        dict.__setitem__(self, k, v)
    else:
      dict.__setitem__(self, key, value)
    return self

  def __str__(self):
    """Readable string representation of `self`.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    assert (str(pd) ==
            "{'bar': 2.0, 'baz': 'three', 'foo': 1}")
    ```

    Returns:
      If the keys in `self` are sortable, returns a string with key/value pairs
      sorted by key. Otherwise, returns a normal `dict.__str__`
      representation.
    """
    try:
      delim = ', ' if len(self) < 8 else ',\n '
      s = delim.join('%s: %s' % (repr(k), repr(self[k])) for k in self.peys())
      return '{' + s + '}'
    except Exception:
      return dict.__str__(self)

  __repr__ = __str__

  def update(self, *a, **kw):
    """Update `self`. **Returns `self` to allow chaining.**

    Examples:
    ```python
    pd = pdict()
    assert (pd.update(foo=1, bar=2.0).foo == 1)
    assert (pd.bar == 2.0)
    assert (pd.update({'baz': 'three'}).baz == 'three')
    ```

    Args:
      *a: Positional args passed to `dict.update`.
      **kw: Keyword args pass to `dict.update`.

    Returns:
      `self` to allow chaining.
    """
    dict.update(self, *a, **kw)
    return self

  def copy(self):
    """Copy `self` to new `defaultpdict`. Performs a shallow copy.

    Examples:
    ```python
    pd1 = pdict(foo=1, bar=2.0, baz='three')
    pd2 = pd1.copy()
    assert (pd2 == pd1)
    assert (pd2 is not pd1)
    ```

    Returns:
      A `pdict` that is a shallow copy of `self`.
    """
    return pdict(dict.copy(self))

  def peys(self):
    """Get `self.keys()` as a sorted `plist`.

    In the common case of a `pdict` with sortable keys, it is often convenient
    to rely on the sort-order of the keys for a variety of operations that would
    otherwise require explicit looping.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    assert (pd.peys().aslist() == ['bar', 'baz', 'foo'])
    pd_str = pdict()
    pd_str[pd.peys()] = pd.palues().pstr()  # Converts the values to strings.
    assert (pd_str ==
            dict(foo='1', bar='2.0', baz='three'))
    ```

    Returns:
      `plist` of keys in sorted order.
    """
    return plist(sorted(self.keys()))

  def palues(self):
    """Equivalent to `self.values()`, but returns a `plist` with values sorted as in `self.peys()`.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    assert (pd.palues().aslist() ==
            [2.0, 'three', 1])
    ```

    The `plist` returned is rooted at a corresponding `plist` of `KeyValue` `namedtuple`s,
    allowing easy recovery of an equivalent `pdict`, possibly after modifications to the
    values:
    ```python
    pd_str = (pd.palues().pstr() + ' foo').pdict()
    assert (pd_str ==
            dict(foo='1 foo', bar='2.0 foo', baz='three foo'))
    ```

    Returns:
      `plist` of values from `self`, in the same order given by `self.peys()`.
      The `root()` of the `plist` is `KeyValue` `namedtuple`s from `self`.
    """
    return self[self.peys()]

  def pitems(self):
    """Equivalent to `self.items()`, but returns a `plist` with items sorted as in `self.peys()`.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    assert (pd.pitems().aslist() ==
            [('bar', 2.0), ('baz', 'three'), ('foo', 1)])
    assert (pd.pitems().key.aslist() ==
            pd.peys().aslist())
    assert (pd.pitems().value.aslist() ==
            pd.palues().aslist())
    ```
    In the example above, note that the items are `KeyValue` `namedtuple`s,
    so the first element can be accessed with `.key` and the second with `.value`.

    Returns:
      `plist` of items from `self`, in the same order given by `self.peys()`.
    """
    return self.palues().root()

  def qj(self, *a, **kw):
    """Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

    `qj` is a debug logging function. Calling `pdict.qj()` is often the fastest way
    to begin debugging an issue.

    See [qj](https://github.com/iansf/qj) for detailed information on using `qj`.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    pd.qj('pd').update(baz=3).qj('pd now')
    assert (pd.baz == 3)
    # Logs:
    # qj: <calling_module> calling_function: pd <2910>: {'bar': 2.0, 'baz': 'three', 'foo': 1}
    # qj: <calling_module> calling_function:  pd now <2910>: {'bar': 2.0, 'baz': 3, 'foo': 1}
    ```

    Returns:
      `self`, as processed by the arguments supplied to `qj`.
    """
    depth = kw.pop('_depth', 0) + 2
    return qj(self, _depth=depth, *a, **kw)

  def rekey(self, map_or_fn, inplace=False):
    """Change the keys of `self` or a copy while keeping the same values.

    Convenience method for renaming keys in a `pdict`. Passing a `dict` mapping
    old keys to new keys allows easy selective renaming, as any key not in the
    `dict` will be unchanged. Passing a `callable` requires you to return a unique
    value for every key in `self`

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    assert (pd.rekey(dict(foo='floo')) ==
            dict(floo=1, bar=2.0, baz='three'))
    assert (pd.foo == 1)  # pd is unmodified by default.
    pd.rekey(dict(bar='car'), True)
    assert ('bar' not in pd)
    assert (pd.car == 2.0)

    pd.rekey(lambda k: 'far' if k == 'car' else k, True)
    assert ('car' not in pd)
    assert (pd.far == 2.0)
    ```

    Returns:
      `self` if `inplace` evaluates to `True`, otherwise a new `pdict`. The keys will
      be changed, but the values will remain the same.

    Raises:
      ValueError: If `map_or_fn` isn't a `dict` or a `callable`.
      ValueError: If `map_or_fn` fails to generate a unique key for every key in `self`.
    """
    if not inplace:
      return self.copy().rekey(map_or_fn, inplace=True)
    if isinstance(map_or_fn, dict):
      func = lambda k: map_or_fn.get(k, k)
    else:
      func = map_or_fn
    if not callable(func):
      raise ValueError('`map_or_fn` must be a dict or callable. Received %s: %s'
                       % (str(type(map_or_fn)), str(map_or_fn)))
    keys = self.peys()
    new_keys = keys.apply(func).puniq()
    if len(keys) != len(new_keys):
      raise ValueError('rekey map must return the same number of unique keys as the original pdict. '
                       'Only found %d of %d expected keys.' % (len(new_keys), len(keys)))
    vals = self.palues().uproot()
    self.clear()
    self[new_keys] = vals
    return self


################################################################################
################################################################################
################################################################################
# defaultpdict class
################################################################################
################################################################################
################################################################################
class defaultpdict(defaultdict):
  """`defaultdict` subclass where everything is automatically a property.

  Examples:

  Use with dot notation or subscript notation:
  ```python
    p = defaultpdict()
    p.foo = 1
    assert (p['foo'] == p.foo == 1)
  ```

  Set the desired default constructor as normal to avoid having to construct
  individual values:
  ```python
    p = defaultpdict(int)
    assert (p.foo == 0)
  ```

  `list` subscripts also work and return a `plist` of the corresponding keys:
  ```python
    p = defaultpdict(foo=1, bar=2)
    assert (p[['foo', 'bar']].aslist() == [1, 2])
  ```

  Setting with a `list` subscript also works, using a single element or a matching
  `list` for the values:
  ```python
    p = defaultpdict()
    p[['foo', 'bar']] = 1
    assert (p[['foo', 'bar']].aslist() == [1, 1])
    p[['foo', 'bar']] = [1, 2]
    assert (p[['foo', 'bar']].aslist() == [1, 2])
  ```

  `defaultpdict.update()` returns `self`, rather than `None`, to support chaining:
  ```python
    p = defaultpdict(foo=1, bar=2)
    p.update(bar=3).baz = 4
    assert (p.bar == 3)
    assert ('baz' in p.keys())
  ```

  Nested `defaultpdict`s make nice lightweight objects:
  ```python
    p = defaultpdict(lambda: defaultpdict(list))
    p.foo = 1
    p.stats.bar.append(2)
    assert (p['foo'] == 1)
    assert (p.stats.bar == [2])
  ```
  """

  def __init__(self, *a, **kw):
    """Initialize `defaultpdict`.

    Examples:
    ```python
    pd = defaultpdict(int)
    assert (pd.foo == 0)
    pd.bar += 10
    assert (pd.bar == 10)

    pd = defaultpdict(lambda: defaultpdict(list))
    pd.foo.bar = 20
    assert (pd == dict(foo=dict(bar=20)))
    pd.stats.bar.append(2)
    assert (pd.stats.bar == [2])
    ```

    Args:
      *a: Positional arguments passed through to `defaultdict()`.
      **kw: Keyword arguments pass through to `defaultdict()`.

    Returns:
      `None`. `defaultpdict` is initialized.
    """
    defaultdict.__init__(self, *a, **kw)

  def __getattr__(self, name):
    """Override `getattr`. If `name` starts with '_', attempts to find that attribute on `self`. Otherwise, looks for a field of that name in `self`.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (pd.foo == 1)
    assert (pd.__module__.startswith('pstar'))
    ```

    Args:
      name: A field name or property name on `self`.

    Returns:
      Value at `self.<name>` or `self[name]`.
    """
    if name.startswith('_'):
      return defaultdict.__getattribute__(self, name)
    return self[name]

  def __setattr__(self, name, value):
    """Attribute assignment operation. Forwards to subscript assignment.

    Permits `pdict`-style field assignment.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    pd.floo = 4.0
    assert (pd.floo == pd['floo'] == 4.0)
    ```

    Args:
      name: Any `hash`able value or list of `hash`able values, as in `defaultpdict.__setitem__`,
            but generally just a valid identifier string provided by the compiler.
      value: Any value, or `plist` of values of the same length as the corresponding list in
             `name`.

    Returns:
      `self` to allow chaining through direct calls to `defaultpdict.__setattr__`.
    """
    self[name] = value
    return self

  def __getitem__(self, key):
    """Subscript operation. Keys can be any normal `dict` keys or `list`s of such keys.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (pd['foo'] == pd.foo == 1)
    assert (pd[['foo', 'bar', 'baz']].aslist() == [1, 2.0, 'three'])
    ```

    When indexing with a `list`, the returned `plist` is rooted at a `plist` of
    `KeyValue` `namedtuple`s, making it easy to recover the keys that gave the values, and
    allows the `plist` to be turned back into a corresponding `pdict`:
    ```python
    assert (pd[['foo', 'baz']].root().aslist() ==
            [('foo', 1), ('baz', 'three')])
    assert (pd[['foo', 'baz']].pdict() ==
            dict(foo=1, baz='three'))
    ```

    Args:
      key: Any `hash`able object, or a `list` of `hash`able objects.

    Returns:
      Either the value held at `key`, or a `plist` of values held at each key in the `list`
      of keys, when called with a `list` of keys.
    """
    if isinstance(key, list):
      return plist([self[k] for k in key], root=plist([KeyValue(k, self[k]) for k in key]))
    else:
      return defaultdict.__getitem__(self, key)

  def __setitem__(self, key, value):
    """Subscript assignment operation. Keys and values can be scalars or `list`s.

    Examples:

    `defaultpdict` assignment works normally for any `hash`able `key`:
    ```python
    pd = defaultpdict(int)
    pd['foo'] = 1
    assert (pd.foo == pd['foo'] == 1)
    ```

    `defaultpdict` assignment can also work with a `list` of `hash`able `key`s:
    ```python
    pd[['bar', 'baz']] = plist[2.0, 'three']
    assert (pd.bar == pd['bar'] == 2.0)
    assert (pd.baz == pd['baz'] == 'three')
    ```

    Args:
      key: Any `hash`able object, or a `list` of `hash`able objects.
      value: Any value, or a `plist` of values that matches the shape of `key`, if it
             is a `list`.

    Returns:
      `self`, to allow chaining with direct calls to `defaultpdict.__setitem__`.
    """
    if isinstance(key, list):
      value = _ensure_len(len(key), value)
      for k, v in zip(key, value):
        defaultdict.__setitem__(self, k, v)
    else:
      defaultdict.__setitem__(self, key, value)
    return self

  def __str__(self):
    """Readable string representation of `self`.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (str(pd) ==
            "{'bar': 2.0, 'baz': 'three', 'foo': 1}")
    ```

    Returns:
      If the keys in `self` are sortable, returns a string with key/value pairs
      sorted by key. Otherwise, returns a normal `defaultdict.__str__`
      representation.
    """
    try:
      delim = ', ' if len(self) < 8 else ',\n '
      s = delim.join('%s: %s' % (repr(k), repr(self[k])) for k in self.peys())
      return '{' + s + '}'
    except Exception:
      return defaultdict.__str__(self)

  __repr__ = __str__

  def update(self, *a, **kw):
    """Update `self`. **Returns `self` to allow chaining.**

    Examples:
    ```python
    pd = defaultpdict(int)
    assert (pd.update(foo=1, bar=2.0).foo == 1)
    assert (pd.bar == 2.0)
    assert (pd.update({'baz': 'three'}).baz == 'three')
    ```

    Args:
      *a: Positional args passed to `defaultdict.update`.
      **kw: Keyword args passed to `defaultdict.update`.

    Returns:
      `self` to allow chaining.
    """
    defaultdict.update(self, *a, **kw)
    return self

  def copy(self):
    """Copy `self` to new `defaultpdict`. Performs a shallow copy.

    Examples:
    ```python
    pd1 = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    pd2 = pd1.copy()
    assert (pd2 == pd1)
    assert (pd2 is not pd1)
    ```

    Returns:
      A `defaultpdict` that is a shallow copy of `self`.
    """
    return defaultdict.copy(self)

  def peys(self):
    """Get `self.keys()` as a sorted `plist`.

    In the common case of a `defaultpdict` with sortable keys, it is often convenient
    to rely on the sort-order of the keys for a variety of operations that would
    otherwise require explicit looping.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (pd.peys().aslist() == ['bar', 'baz', 'foo'])
    pd_str = pdict()
    pd_str[pd.peys()] = pd.palues().pstr()  # Converts the values to strings.
    assert (pd_str ==
            dict(foo='1', bar='2.0', baz='three'))
    ```

    Returns:
      `plist` of keys in sorted order.
    """
    return plist(sorted(self.keys()))

  def palues(self):
    """Equivalent to `self.values()`, but returns a `plist` with values sorted as in `self.peys()`.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (pd.palues().aslist() ==
            [2.0, 'three', 1])
    ```

    The `plist` returned is rooted at a corresponding `plist` of `KeyValue` `namedtuple`s,
    allowing easy recovery of an equivalent `pdict`, possibly after modifications to the
    values:
    ```python
    pd_str = (pd.palues().pstr() + ' foo').pdict()
    assert (pd_str ==
            dict(foo='1 foo', bar='2.0 foo', baz='three foo'))
    ```

    Returns:
      `plist` of values from `self`, in the same order given by `self.peys()`.
      The `root()` of the `plist` is `KeyValue` `namedtuple`s from `self`.
    """
    return self[self.peys()]

  def pitems(self):
    """Equivalent to `self.items()`, but returns a `plist` with items sorted as in `self.peys()`.

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (pd.pitems().aslist() ==
            [('bar', 2.0), ('baz', 'three'), ('foo', 1)])
    assert (pd.pitems().key.aslist() ==
            pd.peys().aslist())
    assert (pd.pitems().value.aslist() ==
            pd.palues().aslist())
    ```
    In the example above, note that the items are `KeyValue` `namedtuple`s,
    so the first element can be accessed with `.key` and the second with `.value`.

    Returns:
      `plist` of items from `self`, in the same order given by `self.peys()`.
    """
    return self.palues().root()

  def qj(self, *a, **kw):
    """Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

    `qj` is a debug logging function. Calling `defaultpdict.qj()` is often the fastest way
    to begin debugging an issue.

    See [qj](https://github.com/iansf/qj) for detailed information on using `qj`.

    Examples:
    ```python
    pd = pdict(foo=1, bar=2.0, baz='three')
    pd.qj('pd').update(baz=3).qj('pd now')
    assert (pd.baz == 3)
    # Logs:
    # qj: <calling_module> calling_function: pd <2910>: {'bar': 2.0, 'baz': 'three', 'foo': 1}
    # qj: <calling_module> calling_function:  pd now <2910>: {'bar': 2.0, 'baz': 3, 'foo': 1}
    ```

    Returns:
      `self`, as processed by the arguments supplied to `qj`.
    """
    depth = kw.pop('_depth', 0) + 2
    return qj(self, _depth=depth, *a, **kw)

  def rekey(self, map_or_fn, inplace=False):
    """Change the keys of `self` or a copy while keeping the same values.

    Convenience method for renaming keys in a `defaultpdict`. Passing a `dict` mapping
    old keys to new keys allows easy selective renaming, as any key not in the
    `dict` will be unchanged. Passing a `callable` requires you to return a unique
    value for every key in `self`

    Examples:
    ```python
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    assert (pd.rekey(dict(foo='floo')) ==
            dict(floo=1, bar=2.0, baz='three'))
    assert (pd.foo == 1)  # pd is unmodified by default.
    pd.rekey(dict(bar='car'), True)
    assert ('bar' not in pd)
    assert (pd.car == 2.0)

    pd.rekey(lambda k: 'far' if k == 'car' else k, True)
    assert ('car' not in pd)
    assert (pd.far == 2.0)
    ```

    Returns:
      `self` if `inplace` evaluates to `True`, otherwise a new `defaultpdict`. The keys will
      be changed, but the values will remain the same.

    Raises:
      ValueError: If `map_or_fn` isn't a `dict` or a `callable`.
      ValueError: If `map_or_fn` fails to generate a unique key for every key in `self`.
    """
    if not inplace:
      return self.copy().rekey(map_or_fn, inplace=True)
    if isinstance(map_or_fn, dict):
      func = lambda k: map_or_fn.get(k, k)
    else:
      func = map_or_fn
    if not callable(func):
      raise ValueError('`map_or_fn` must be a dict or callable. Received %s: %s'
                       % (str(type(map_or_fn)), str(map_or_fn)))
    keys = self.peys()
    new_keys = keys.apply(func).puniq()
    if len(keys) != len(new_keys):
      raise ValueError('rekey map must return the same number of unique keys as the original pdict. '
                       'Only found %d of %d expected keys.' % (len(new_keys), len(keys)))
    vals = self.palues().uproot()
    self.clear()
    self[new_keys] = vals
    return self


################################################################################
################################################################################
################################################################################
# pset class
################################################################################
################################################################################
################################################################################
class pset(frozenset):
  """Placeholder frozenset subclass. Not yet implemented."""
  pass


################################################################################
################################################################################
################################################################################
# plist method builder functions.
################################################################################
################################################################################
################################################################################
def _build_comparator(op, merge_op, shortcut, return_root_if_empty_other):
  """Builds a plist comparator operation.

  Args:
    op: Comparison operation, such as operator.__eq__.
    merge_op: Set-like operation for merging sets of intermediate results, such
              as operator.__and__.
    shortcut: Function to call to shortcut comparison if `self is other`.
    return_root_if_empty_other: Boolean for how to handle `other` being an empty
                                list. If `True`, `self.__root__` is returned. If
                                `False`, an empty plist is returned.

  Returns:
    comparator: The comparison function.
  """
  def comparator(self, other, return_inds=False):
    """`plist` comparison operator. **Comparisons filter plists.**

    **IMPORTANT:** `plist` comparisons all filter the `plist` and return a new
    `plist`, rather than a truth value.

    `comparator` is not callable directly from `plist`. It implements the various
    python comparison operations: `==`, `<`, `>`, etc. The comparison operators
    can be called directly with their corresponding 'magic' functions,
    `plist.__eq__`, `plist.__lt__`, `plist.__gt__`, etc., but are generally just
    called implicitly.

    Examples:
    `plist` comparators can filter on leaf values:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    zero_bars = foo.bar == 0
    assert (zero_bars.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    nonzero_bars = foo.bar != 0
    assert (nonzero_bars.aslist() ==
            [{'foo': 1, 'bar': 1}])
    ```

    They can also filter on other plists so long as the structures are
    compatible:
    ```python
    assert ((foo == zero_bars).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    assert ((foo.foo > foo.bar).aslist() ==
            [{'foo': 2, 'bar': 0}])
    ```

    The same is true when comparing against lists with compatible structure:
    ```python
    assert ((foo.foo == [0, 1, 3]).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    ```

    This all generalizes naturally to plists that have been grouped:
    ```python
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    nonzero_foo_by_bar_foo = foo_by_bar_foo.bar > 0
    assert (nonzero_foo_by_bar_foo.aslist() ==
            [[[],
              []],
             [[{'bar': 1, 'foo': 1}]]])
    zero_foo_by_bar_foo = foo_by_bar_foo.foo != nonzero_foo_by_bar_foo.foo
    assert (zero_foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    assert ((foo_by_bar_foo.foo == [[[0], [3]], [[1]]]).aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              []],
             [[{'foo': 1, 'bar': 1}]]])
    ```

    Lists with incompatible structure are compared to `self` one-at-a-time,
    resulting in set-like filtering where the two sets are merged with an 'or':
    ```python

    assert ((foo.foo == [0, 1, 3, 4]).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])

    assert ((foo_by_bar_foo.foo == [0, 1, 3, 4]).aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              []],
             [[{'foo': 1, 'bar': 1}]]])
    ```

    When comparing against an empty list, `==` always returns an empty list, but
    all other comparisons return `self`:
    ```python
    assert ((foo.foo == []).aslist() == [])
    assert ((foo.foo < []).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert ((foo_by_bar_foo == nonzero_foo_by_bar_foo).aslist() ==
            [[[],
              []],
             [[{'foo': 1, 'bar': 1}]]])
    assert ((foo_by_bar_foo.foo > nonzero_foo_by_bar_foo.foo).aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    ```

    Note that `plist.nonempty` can be used to remove empty internal `plist`s
    after filtering a grouped `plist`:
    ```python
    assert ((foo_by_bar_foo == nonzero_foo_by_bar_foo).nonempty(-1).aslist() ==
            [[[{'foo': 1, 'bar': 1}]]])
    ```

    Args:
      other: Object to compare against.
      return_inds: Optional bool. When `True`, causes the comparison to return
                   the plist indices of the matching items. When `False`
                   (the default), causes the comparison to return a plist of the
                   matching values.

    Returns:
      A new plist, filtered from `self` and `other` according to the operation
      provided to `_build_comparator`, if `return_inds` is `False`. Otherwise,
      returns the corresponding indices into self.
    """
    if self is other:
      return shortcut(self, return_inds)
    inds = []
    if isinstance(other, list):
      if len(self) == len(other):
        for i, (x, o) in enumerate(zip(self, other)):
          if isinstance(x, plist):
            child_inds = comparator(x, o, return_inds=True)
            inds.append(child_inds)
          elif op(x, o):
            inds.append(i)
      elif len(other) > 0:
        inds = comparator(self, other[0], return_inds=True)
        for o in other[1:]:
          inds = _merge_indices(inds, comparator(self, o, return_inds=True), merge_op)
      else:
        # len(other) == 0
        if return_inds:
          inds = self.lfill(pepth=-1) if return_root_if_empty_other else []
        else:
          return self.__root__ if return_root_if_empty_other else plist()
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = comparator(x, other, return_inds=True)
          inds.append(child_inds)
        elif op(x, other):
          inds.append(i)

    if return_inds:
      return inds

    return self.__root__[inds]

  return comparator


def _build_logical_op(op):
  """Builds a `plist` logical operation.

  Args:
    op: Logical operation, such as operator.__and__.

  Returns:
    logical_op: The logical operation function.
  """
  def logical_op(self, other):
    """`plist` logical operation. **Logical operations perform set operations on `plist`s.**

    **IMPORTANT:** `plist` logical operations between two `plist`s perform `set` operations
    on the two `plist`s. Logical operations between a `plist` and any other type attempts
    to perform that operation on the values in the `plist` and `other` itself.

    `logical_op` is not callable directly from `plist`. It implements the various
    python logical operations: `&`, `|`, `^`, etc. The logical operators
    can be called directly with their corresponding 'magic' functions,
    `plist.__and__`, `plist.__or__`, `plist.__xor__`, etc., but are generally just
    called implicitly.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    assert (((foos.bar == 0) & (foos.baz == 3)).aslist() ==
            [{'baz': 3, 'foo': 0, 'bar': 0}])

    assert (((foos.bar == 0) | (foos.baz == 3)).aslist() ==
            [{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}])

    assert (((foos.bar == 0) ^ (foos.baz == 3)).aslist() ==
            [{'bar': 0, 'baz': 5, 'foo': 2}])

    by_bar = foos.bar.groupby()

    assert (((by_bar.bar == 0) & (by_bar.bar == 1)).aslist() ==
            [[], []])
    assert (((by_bar.bar == 0) & (by_bar.bar <= 1)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}], []])

    assert (((by_bar.baz == 3) | (by_bar.baz == 6)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
    assert (((by_bar.baz == 6) | (by_bar.baz <= 4)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])

    assert (((by_bar.baz == 3) ^ (by_bar.baz == 6)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
    assert (((by_bar.baz == 6) ^ (by_bar.bar <= 4)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}], []])
    ```

    Logical operations can be applied element-wise if `other` is not a `plist`:
    ```python
    assert ((foos.baz & 1).aslist() ==
            [1, 0, 1])
    assert ((by_bar.baz | 1).aslist() ==
            [[3, 5], [7]])
    assert ((1 ^ by_bar.baz).aslist() ==
            [[2, 4], [7]])
    ```

    Args:
      other: Object to perform the logical operation with.

    Returns:
      New `plist`, merging `self` and `other` according to the operation provided
      to `_build_logical_op`.
    """
    if isinstance(other, plist):
      if len(self) == len(other):
        try:
          return plist([op(x, o) for x, o in zip(self, other)])
        except Exception:
          pass
      self_flat = self.ungroup(-1)
      other_flat = other.ungroup(-1)
      ids = op(set([id(x) for x in self_flat]),
               set([id(x) for x in other_flat]))
      if op is operator.__and__ or op is operator.__iand__:
        return plist([x for x in self_flat if id(x) in ids])  # Don't pass root -- we are uprooting
      else:
        return plist(
            [ids.remove(id(x)) or x for x in self_flat if id(x) in ids] +
            [ids.remove(id(x)) or x for x in other_flat if id(x) in ids]
        )  # Don't pass root -- we are uprooting
    else:
      return plist([op(x, other) for x in self], root=self.__root__)

  return logical_op


def _build_binary_op(op):
  """Builds a plist binary operation.

  Args:
    op: Binary operation, such as operator.__add__.

  Returns:
    binary_op: The binary operation function.
  """
  def binary_op(self, other):
    """`plist` binary operation; applied element-wise to `self`.

    `binary_op` is not callable directly from `plist`. It implements the various
    python binary operations: `+`, `-`, `*`, etc. The binary operators
    can be called directly with their corresponding 'magic' functions,
    `plist.__add__`, `plist.__sub__`, `plist.__mul__`, etc., but are generally just
    called implicitly.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    assert ((foos.foo + foos.baz).aslist() ==
            [3, 7, 7])
    assert ((2 * (foos.foo + 7)).aslist() ==
            [14, 16, 18])

    by_bar = foos.bar.groupby()

    assert ((by_bar.foo + by_bar.baz).aslist() ==
            [[3, 7], [7]])
    assert ((2 * (by_bar.foo + 7)).aslist() ==
            [[14, 18], [16]])
    ```

    The only binary operation that doesn't work as expected is string interpolation:
    `'foo: %d' % foos.foo`. This can't work as expected because python handles that
    operation in a special manner. However, `+` works on `plist`s of strings, as
    does `plist.apply('{}'.format)`:
    ```python
    assert (('foo: ' + foos.foo.pstr() + ' bar: ' + foos.bar.pstr()).aslist() ==
            ['foo: 0 bar: 0', 'foo: 1 bar: 1', 'foo: 2 bar: 0'])
    assert (foos.foo.apply('foo: {} bar: {}'.format, foos.bar).aslist() ==
            ['foo: 0 bar: 0', 'foo: 1 bar: 1', 'foo: 2 bar: 0'])

    assert (('foo: ' + by_bar.foo.pstr() + ' bar: ' + by_bar.bar.pstr()).aslist() ==
            [['foo: 0 bar: 0', 'foo: 2 bar: 0'], ['foo: 1 bar: 1']])
    assert (by_bar.foo.apply('foo: {} bar: {}'.format, by_bar.bar).aslist() ==
            ['foo: [0, 2] bar: [0, 0]', 'foo: [1] bar: [1]'])
    assert (by_bar.foo.apply_('foo: {} bar: {}'.format, by_bar.bar).aslist() ==
            [['foo: 0 bar: 0', 'foo: 2 bar: 0'], ['foo: 1 bar: 1']])
    ```
    Note the difference between the final two examples using `apply()` vs. `apply_()` on
    grouped `plist`s.

    Args:
      other: Object to perform the binary operation with.

    Returns:
      A new plist, where each element of `self` had the operation passed to
      `_build_binary_op` applied to it and `other`, or the corresponding element
      of `other`, if the lengths of `self` and `other` match.
    """
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([op(x, o) for x, o in zip(self, other)], root=self.__root__)
      else:
        qj((len(self), len(other)))
    return plist([op(x, other) for x in self], root=self.__root__)

  return binary_op


def _build_binary_rop(op):
  """Builds a plist binary operation where the plist is only the right side.

  Args:
    op: Left-side binary operation, such as operator.__add__.

  Returns:
    binary_rop: The corresponding right-side binary operation function.
  """
  def binary_rop(self, other):
    return plist([op(other, x) for x in self], root=self.__root__)

  return binary_rop


def _build_binary_ops(op, iop):
  """Builds all three variants of plist binary operation: op, rop, and iop.

  Args:
    op: Binary operation, such as operator.__add__.
    iop: Binary assignment operation, such as operator.__iadd__.

  Returns:
    The plist binary operation and its right-side and assignment variants.
  """
  return _build_binary_op(op), _build_binary_rop(op), _build_binary_op(iop)


def _build_unary_op(op):
  """Builds a plist unary operation.

  Args:
    op: Unary operation, such as operator.__neg__.

  Returns:
    unary_op: The unary operation function.
  """
  def unary_op(self):
    """`plist` unary operation; applied element-wise to `self`.

    `unary_op` is not callable directly from `plist`. It implements the various
    python unary operations: `-`, `~`, `abs`, etc. The unary operators
    can be called directly with their corresponding 'magic' functions,
    `plist.__neg__`, `plist.__invert__`, `plist.__abs__`, etc., but are generally just
    called implicitly.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    assert ((-foos.foo).aslist() ==
            [0, -1, -2])
    assert ((~foos.foo).aslist() ==
            [-1, -2, -3])

    by_bar = foos.bar.groupby()

    assert ((-by_bar.foo).aslist() ==
            [[0, -2], [-1]])
    assert ((~by_bar.foo).aslist() ==
            [[-1, -3], [-2]])
    ```

    Returns:
      A new `plist`, where each element of `self` had the operation passed to
      `_build_unary_op` applied to it.
    """
    return plist([op(x) for x in self], root=self.__root__)

  return unary_op


################################################################################
################################################################################
################################################################################
# plist helper functions and constants.
################################################################################
################################################################################
################################################################################
if sys.version_info[0] < 3:
  STRING_TYPES = types.StringTypes
  PLIST_CALL_ATTR_CALL_PEPTH_DELTA = 1
else:
  STRING_TYPES = str
  PLIST_CALL_ATTR_CALL_PEPTH_DELTA = 2

NONCALLABLE_ATTRS = ['__class__', '__dict__', '__doc__', '__module__']


def _call_attr(_pobj, _pname, _pattr, *_pargs, **_pkwargs):
  """Recursive function to call the desired attribute.

  Args:
    _pobj: Object that the attribute will be called on. May not be a plist
           if `pepth != 0`.
    _pname: Name of the attribute being called.
    _pattr: Bound attribute found by a `__getattribute__` or `getattr` call.
    *_pargs: Arguments passed directly to the attribute.
    **_pkwargs: Keyword arguments passed directly to the attribute, except
                `pepth`, `call_pepth`, and `psplit`, which are removed.
                `pepth` tracks the desired depth in the plist of the
                attribute. When `pepth == 0`, the attribute is called or
                returned (for non-callable attributes).
                `call_pepth` tracks the actual depth the call occurs at. It is
                only passed on to a known list of plist methods that need it
                in order to correctly handle stack frames between the original
                caller and the final call.
                `psplit` causes calling to happen in parallel, with the same
                semantics as in `plist.apply`.

  Returns:
    Either the value of the attribute, if the attribute is a known
    non-callable attribute, or the value of calling the attribute with the
    provided arguments.
  """
  pepth = _pkwargs.pop('pepth', 0)
  call_pepth = _pkwargs.pop('call_pepth', 0)
  psplit = _pkwargs.pop('psplit', 0)

  if pepth != 0:
    if not isinstance(_pobj, plist):
      if _pname in NONCALLABLE_ATTRS:
        return _pattr
      return _pattr(*_pargs, **_pkwargs)
    pargs = [_ensure_len(len(_pobj), a, strict=True) for a in _pargs]
    pkwargs = {
        k: _ensure_len(len(_pobj), v, strict=True) for k, v in _pkwargs.items()
    }
    try:
      attrs = [list.__getattribute__(x, _pname) if isinstance(x, list) else getattr(x, _pname) for x in _pobj]

      if psplit > 0 and isinstance(_pobj, plist):
        pool = _get_thread_pool(psplit, len(_pobj))

        call_args = [pdict(x=x, i=i) for i, x in enumerate(_pobj)]
        map_func = lambda ca: _call_attr(ca.x,
                                         _pname, attrs[ca.i],
                                         pepth=pepth - 1,
                                         call_pepth=0,  # It's not possible to get the proper stack frame when spinning off threads, so don't bother tracking it.
                                         psplit=psplit,
                                         *[a[ca.i] for a in pargs],
                                         **{k: v[ca.i] for k, v in pkwargs.items()})
        return plist(pool.map(map_func, call_args, chunksize=_get_thread_chunksize(psplit, len(_pobj))), root=_pobj.__root__)
      return plist([_call_attr(x,
                               _pname,
                               attrs[i],
                               pepth=pepth - 1,
                               call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA,
                               psplit=psplit,
                               *[a[i] for a in pargs],
                               **{k: v[i] for k, v in pkwargs.items()})
                    for i, x in enumerate(_pobj)],
                   root=_pobj.__root__)
    except Exception as e:
      if pepth > 0:
        raise e

  if isinstance(_pobj, plist) and _pname in ['qj', 'me']:
    result = _pattr(call_pepth=call_pepth, *_pargs, **_pkwargs)
  elif psplit > 0 and isinstance(_pobj, plist) and _pname == 'apply':
    result = _pattr(psplit=psplit, *_pargs, **_pkwargs)
  elif _pname == 'qj':
    depth = _pkwargs.pop('_depth', 0) + call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA + (sys.version_info[0] < 3)
    result = _pattr(_depth=depth, *_pargs, **_pkwargs)
  elif _pname in NONCALLABLE_ATTRS:
    return _pattr
  else:
    result = _pattr(*_pargs, **_pkwargs)

  if result is None and isinstance(_pobj, plist):
    return _pobj
  return result


def _ensure_len(length, x, strict=False):
  """Convert `x` to a `list` of length `length` if necessary and return it.

  This function is the core of `plist` 'deepcasting', which is conceptually
  similar to 'broadcasting' in `numpy` and `tensorflow`, but is intentionally much
  more permissive. Deepcasting relies on the fact that most functions will
  crash if they receive a `list` when they were expecting a scalar value. Allowing
  the called function to crash, rather than crashing in `plist`, allows `plist` to
  be optimistic, and avoids `plist` having to guess how a user-supplied function
  is meant to be called.

  Args:
    length: int.
    x: object to convert.
    strict: Boolean. If `True`, only `plist`s are returned without being wrapped.
            `list`s and other iterables of the correct length are still returned
            wrapped in a new `list` of the correct length. Defaults to `False`,
            which means that `list`s and other iterables of the correct length
            are returned unchanged.

  Returns:
    `x` if `x` is a non-string sequence and `len(x) == length`.
    Otherwise a list with `length` copies of `x`.
  """
  if ((strict
       and isinstance(x, plist) and len(x) == length)
      or (not strict
          and not isinstance(x, type)
          and not isinstance(x, STRING_TYPES)
          and not isinstance(x, tuple)
          and hasattr(x, '__len__')
          and len(x) == length)):
    return x
  return [x for _ in range(length)]


def _merge_indices(left, right, op):
  """Merge index arrays using set operation `op`.

  This is the core of the filtering that happens in the plist comparators.

  Args:
    left: List of integer indices.
    right: List of integer indices.
    op: Set operation to merge the two lists. E.g., operator.__and__.

  Returns:
    List containing merged indices.
  """
  try:
    left_empty_or_ints = len(left) == 0 or plist(left).all(isinstance, int)
    right_empty_or_ints = len(right) == 0 or plist(right).all(isinstance, int)
    if left_empty_or_ints and right_empty_or_ints:
      sl = set(left)
      sr = set(right)
      return sorted(list(op(sl, sr)))
  except Exception:
    pass
  try:
    return [_merge_indices(left[i], right[i], op) for i in range(max(len(left), len(right)))]
  except Exception:
    pass
  if isinstance(left, list) and isinstance(right, list):
    return left.extend(right) or left
  return [left, right]


def _successor(v):
  """Returns a successor/predecessor object starting at value v."""
  s = pdict(v=v, p=lambda: s.update(v=s.v - 1).v, s=lambda: s.update(v=s.v + 1).v)
  return s


class _SyntaxSugar(type):
  def __getitem__(cls, key):
    return plist(key)


MAX_THREADS = 25
def _get_thread_pool(psplit, obj_len):
  return Pool(psplit if psplit > 1 else min(MAX_THREADS, obj_len))


def _get_thread_chunksize(psplit, obj_len):
  return max(1, obj_len // psplit) if psplit > 1 else 1


################################################################################
################################################################################
################################################################################
# plist class
################################################################################
################################################################################
################################################################################
class plist(compatible_metaclass(_SyntaxSugar, list)):
  """List where everything is automatically a property that is applied to its elements. Guaranteed to surprise, if not delight.

  See README.md for a detailed overview of ways plist can be used.
  See tests/pstar_test.py for usage examples ranging from simple to complex.
  """

  __slots__ = ['__root__', '__pepth__']

  def __init__(self, *args, **kwargs):
    """Constructs plist.

    Args:
      *args: Passed directly to list constructor.
      **kwargs: Should only contain 'depth' and 'root' as optional keywords. All
                other keys are passed directly to list constructor.

    Returns:
      None. plist is initialized.
    """
    self.__pepth__ = 0
    depth = kwargs.pop('depth', 1)
    self.__root__ = kwargs.pop('root', self)
    if depth == 1:
      list.__init__(self, *args, **kwargs)
    else:
      # Don't pass root through when making nested plists, because that doesn't make any sense.
      plist.__init__(self, [plist(*args, depth=depth - 1, **kwargs)])  # pylint: disable=non-parent-init-called

  ##############################################################################
  ##############################################################################
  ##############################################################################
  # Private methods.
  ##############################################################################
  ##############################################################################
  ##############################################################################

  def __getattribute__(self, name):
    """Returns a plist of the attribute for self, or for each element.

    If `name` exists as an attribute of plist, that attribute is returned.
    Otherwise, removes trailing underscores from `name` (apart from those
    normally part of a `__*__` name), and uses the count of underscores to
    indicate how deep into the plist `name` should be searched for. Attempts
    to find the modified `name` on plist first, and then looks for `name` on
    each element of self.

    When attempting to find `name` on the elements of self, first it checks
    if the elements all have `name` as an attribute. If so, it returns that
    attribute (`[getattr(x, name) for x in self]`). Otherwise, it attempts to
    return `name` as an index of each element (`[x[name] for x in self]`).

    Examples:

    A `plist` of `list`s has `append` methods at two levels -- the `plist`
    and the contained `list`s. To chose `list.append` them, you can add
    an '_' to the method name:
    ```python
    pl = plist[[1, 2, 3], [4, 5, 6]]
    pl.append([7, 8, 9])
    assert (pl.aslist() ==
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    pl.append_(10)
    assert (pl.aslist() ==
            [[1, 2, 3, 10], [4, 5, 6, 10], [7, 8, 9, 10]])
    ```

    Grouped `plist`s also have methods that you might want to call at different
    depths. Adding an '_' for each layer of the `plist` you want to skip
    allows you to control which depth the method is executed at:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()

    assert (by_bar.foo.apply(str).aslist() ==
            ['[0, 2]', '[1]'])
    assert (by_bar.foo.apply_(str).aslist() ==
            [['0', '2'], ['1']])

    # (Note that it is better to use `plist.pstr` to get string representation of
    # leaf elements:)
    assert (by_bar.foo.pstr().aslist() ==
            [['0', '2'], ['1']])
    ```

    Args:
      name: Name of the attribute.

    Returns:
      Bound `plist` attribute, or `plist` of bound attributes of the elements
      of `self`.

    Raises:
      AttributeError: If `name` is is a reserved member of the elements of `self`.
      AttributeError: If `name` is not found on `self` or the elements of `self`.
    """
    if name == '__root__' or name == '__pepth__':
      return list.__getattribute__(self, name)
    if not name.endswith('___') and name.startswith('__') and name.endswith('__'):
      raise AttributeError('\'%s\' objects cannot call reserved members of their elements: \'%s\'' % (type(self), name))
    try:
      return plist.__getattr__(self, name)
    except AttributeError:
      pass
    if ((name.startswith('__') and name.endswith('___'))
        or (not name.startswith('__') and name.endswith('_'))):
      # Allows calling one level deeper by adding '_' to the end of a property name.  This is recursive, so '__' on the end goes two levels deep, etc.
      # Works for both regular properties (foo.bar_) and private properties (foo.__len___).
      try:
        starting_unders = 2 if name.startswith('__') else 0  # We don't care about single starting underscores for this count
        ending_unders = 0
        for i in range(len(name) - 1, 0, -1):
          if name[i] == '_':
            ending_unders += 1
          else:
            break
        ending_unders -= starting_unders
        return plist.__getattr__(self, name[:-ending_unders], _pepth=ending_unders)
      except AttributeError:
        pass
    try:
      if plist.all(self, hasattr, name):
        return plist([getattr(x, name) for x in self], root=self.__root__)
      return plist([x[name] for x in self], root=self.__root__)
    except Exception as e:
      raise AttributeError('\'%s\' object has no attribute \'%s\' (%s)' % (type(self), name, str(e)))

  ##############################################################################
  # __get*__
  ##############################################################################
  def __getattr__(self, name, _pepth=0):
    """Recursively attempt to get the attribute `name`.

    Handles getting attributes from `self`, rather than from elements of `self`,
    which is handled in `plist.__getattribute__`. The only exception is for
    requests to method names that are present on both `plist` and its leaf
    elements, for example if the leaves are all `list`s, and a sufficiently high
    `_pepth` value, or `_pepth < 0`, in which case the final calls will be
    executed on the leaf elements.

    The attribute gets wrapped in a callable that handles any requested recursion,
    as specified by having called `self._` immediately previously, or due to
    trailing '_' in the name that were detected by `__getattribute__`.

    Args:
      name: Attribute name.
      _pepth: plist depth at which the found attribute should be applied.
              If _pepth < 0, the attribute is applied as deep as possible, which
              may be on the deepest non-plist children. This permits calling,
              for example, list methods on lists nested inside of plists.
              If _pepth > 0, the attribute is applied after that many recursive
              calls, and any exception generated is propogated back.

    Returns:
      Either the value of the attribute, for known non-callable attributes like
      `__class__`, or a callable wrapping the final attributes.
    """
    attr = list.__getattribute__(self, name)

    pepth_local = list.__getattribute__(self, '__pepth__')
    if pepth_local:
      _pepth = pepth_local
      self.__pepth__ = 0

    if _pepth:
      wrap = lambda *a, **k: _call_attr(self, name, attr, pepth=_pepth, *a, **k)
    else:
      wrap = lambda *a, **k: _call_attr(self, name, attr, *a, **k)

    if name in NONCALLABLE_ATTRS or name == '_':
      return wrap()

    return wrap

  def __getitem__(self, key):
    """Returns a new plist using a variety of potential indexing styles.

    TODO

    Args:
      key: The key to index by.
           The key can be applied to self directly as:
             A list of ints: Returns a plist using those ints as indices.
             A slice: Returns a plist based on the slice.
             An int: Returns the value at that index (may not be a plist).
           The key can be applied to elements of self individually:
             A generic list: Returns a plist using the elements of the key in
                             order on the elements of self.
             A tuple when the elements of self can be indexed by tuple:
                      Returns a plist applying that tuple to each element of
                      self.
             A tuple, otherwise:
                      Returns a plist where each element of the new plist is a
                      tuple of each value in the key tuple applied to each
                      element of self. E.g., `foo[('bar', 'baz')]` might return
                      `plist([(1, 2), (3, 4), ...])`.
             Anything else: Returns a plist of the key applied to each of its
                            elements.

    Returns:
      A plist based on the order of attempting to apply the key described above.

    Raises:
      TypeError: If the key fails to be applied directly to self and fails to be
                 applied to its elements individually.
    """
    if self.__pepth__ != 0:
      return plist.__getattr__(self, '__getitem__')(key)
    try:
      if (isinstance(key, list)
          and plist(key).all(isinstance, int)):
        return plist([self[k] for k in key])  # Don't pass root -- we are uprooting
      elif isinstance(key, slice):
        if self is self.__root__:
          return plist(list.__getitem__(self, key))
        return plist(list.__getitem__(self, key), root=plist(list.__getitem__(self.__root__, key)))
      else:
        return list.__getitem__(self, key)
    except TypeError as first_exception:
      try:
        if isinstance(key, list):
          return plist([self[i][k] for i, k in enumerate(key)])  # Don't pass root -- we are uprooting
        if isinstance(key, tuple):
          try:
            return plist([x[key] for x in self], root=self.__root__)
          except Exception:
            return plist([tuple(x[k] for k in key) for x in self], root=self.__root__)
        return plist([x[key] for x in self], root=self.__root__)
      except Exception as second_exception:
        raise TypeError('Failed to apply index to self or elements.\nself exception: %s\nelements exception: %s' % (str(first_exception), str(second_exception)))

  def __getslice__(self, i, j):
    """Delegates to `__getitem__` whenever possible. For compatibility with python 2.7.

    Avoid using `__getslice__` whenever possible in python 2.7, as the bytecode compiler
    assumes that the slice is for the given object on the stack, and modifies negative
    indices relative to that object's length. In `plist`s and other dynamic apis like
    `numpy`, that assumption can cause undetectable and unrecoverable errors.

    To avoid the errors caused by this api in python 2.7, simply use three argument
    slices instead of two; e.g., `plist[::1]`.

    Examples:

    The following examples are safe uses of slicing with `plist`s:
    ```python
    pl = plist['abc', 'def', 'ghi']
    assert (pl[:2:1].aslist() ==
            ['abc', 'def'])
    assert (pl._[:2:1].aslist() ==
            ['ab', 'de', 'gh'])
    ```

    The following example will log a warning -- even though it appears to work, the
    underlying bytecode is incorrect:
    ```python
    assert (pl._[:2].aslist() ==
            ['ab', 'de', 'gh'])
    # Logs:
    #   qj: <pstar> __getslice__: WARNING! <1711>: (multiline log follows)
    #   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
    #   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
    #   This avoids the broken code path in the python compiler.
    ```

    Args:
      i, j: Beginning and ending indices of `slice`.

    Returns:
      `plist` slice of `self`.
    """
    if self.__pepth__ != 0:
      if '__warned__' not in plist.__getslice__.__dict__:
        qj('Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!\n'
           'Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.\n'
           'This avoids the broken code path in the python compiler.', 'WARNING!')
        plist.__getslice__.__dict__['__warned__'] = True
      return plist.__getattr__(self, '__getslice__')(i, j)
    try:
      if self is self.__root__:
        return plist(list.__getslice__(self, i, j))
      return plist(list.__getslice__(self, i, j), root=plist(list.__getslice__(self.__root__, i, j)))
    except Exception:
      return plist.__getitem__(self, slice(i, j))

  ##############################################################################
  # __set*__
  ##############################################################################
  def __setattr__(self, name, val):
    """Sets an attribute on a plist or its elements to `val`.

    TODO

    Args:
      name: Name of the attribute to set.
      val: Value to set the attribute to. If val is a sequence and its length
           matches len(self), the elements of val are set on the elements of
           self. Otherwise, the elements of self are all set to val.

    Returns:
      self, in order to allow chaining through `pl.__setattr__(name, val).foo`.
    """
    if name == '__root__' or name == '__pepth__':
      list.__setattr__(self, name, val)
    elif self.__pepth__ != 0:
      return plist.__setattr__(self, '__setattr__')(name, val)
    else:
      lval = _ensure_len(len(self), val)
      for i, x in enumerate(self):
        x.__setattr__(name, lval[i])
    return self

  def __setitem__(self, key, val):
    """Sets items of self using a variety of potential indexing styles.

    TODO

    Args:
      key: The key to index by.
           The key can be applied to self directly as:
             A list of ints: Sets items using those ints as indices.
             A slice: Sets items based on the slice.
             An int: Sets the item at that index.
           The key can be applied to elements of self individually:
             A generic list: Sets the items of self using the elements of the
                             key in order.
             A tuple when the elements of self can be indexed by tuple:
                      Sets the elements of self using that tuple to index into
                      each element.
             A tuple, otherwise:
                      Sets the elements of self using each element of the tuple
                      key tuple on each element. E.g., `foo[('bar', 'baz')] = 1`
                      will set the `bar` and `baz` keys of `foo` to `1`.
             Anything else: Sets the elements of self indexed by key to `val`.
      val: Value to assign. If val is a sequence and its length matches either
           `len(self)` (in most cases described above for `key`) or `len(key)`,
           each element of val is applied to each corresponding element of
           `self` or `self[k]`.

    Returns:
      self, in order to allow chaining through `pl.__setitem__(key, val).foo`.

    Raises:
      TypeError: If the key fails to be applied directly to self and fails to be
                 applied to its elements individually.
    """
    if self.__pepth__ != 0:
      return plist.__getattr__(self, '__setitem__')(key, val)
    try:
      if (isinstance(key, list)
          and plist(key).all(isinstance, int)):
        lval = _ensure_len(len(key), val)
        for i, k in enumerate(key):
          operator.__setitem__(self, k, lval[i])
      elif isinstance(key, slice):
        lval = val
        if not isinstance(val, collections.Iterable):
          slice_len = len([i for i in range(*key.indices(len(self)))])
          lval = _ensure_len(slice_len, val)
        list.__setitem__(self, key, lval)
      else:
        list.__setitem__(self, key, val)
    except Exception as first_exception:
      try:
        if isinstance(key, list):
          lval = _ensure_len(len(key), val)
          for i, k in enumerate(key):
            operator.__setitem__(self[i], k, lval[i])
        elif isinstance(key, tuple):
          lval = _ensure_len(len(self), val)
          try:
            for i, x in enumerate(self):
              operator.__setitem__(x, key, lval[i])
          except Exception:
            for i, x in enumerate(self):
              for j, k in enumerate(key):
                operator.__setitem__(x, k, lval[i][j])
        else:
          lval = _ensure_len(len(self), val)
          for i, x in enumerate(self):
            operator.__setitem__(x, key, lval[i])
      except Exception as second_exception:
        raise TypeError('Failed to apply index to self or elements.\nself exception: %s\nelements exception: %s' % (str(first_exception), str(second_exception)))

    # Allow chaining of set ops when using apply('__setitem__', k, v) and apply(operators.__setitem__, k, v)
    return self

  def __setslice__(self, i, j, sequence):
    """Delegates to `__setitem__` whenever possible. For compatibility with python 2.7.

    Avoid using `__setslice__` whenever possible in python 2.7, as the bytecode compiler
    assumes that the slice is for the given object on the stack, and modifies negative
    indices relative to that object's length. In `plist`s and other dynamic apis like
    `numpy`, that assumption can cause undetectable and unrecoverable errors.

    To avoid the errors caused by this api in python 2.7, simply use three argument
    slices instead of two; e.g., `plist[::1]`.

    Examples:

    The following examples are safe uses of slicing with `plist`s:
    ```python
    pl = plist['abc', 'def', 'ghi']
    pl[:2:1] = plist['dec', 'abf']
    assert (pl.aslist() ==
            ['dec', 'abf', 'ghi'])

    # Turn strings into mutable lists:
    pl = pl.apply(list)
    # Change slices of the lists:
    pl._[:2:1] = pl._[1:3:1]
    # Turn the lists back into strings
    pl = pl.apply(''.join)
    assert (pl.aslist() ==
            ['ecc', 'bff', 'hii'])
    ```

    The following example will log a warning -- even though it appears to work, the
    underlying bytecode is incorrect:
    ```python
    pl = pl.apply(list)
    pl._[:2] = plist['ab', 'de', 'gh']
    pl = pl.apply(''.join)
    assert (pl.aslist() ==
            ['abc', 'def', 'ghi'])
    # Logs:
    #   qj: <pstar> __setslice__: WARNING! <1711>: (multiline log follows)
    #   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
    #   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
    #   This avoids the broken code path in the python compiler.
    ```

    Args:
      i, j: Beginning and ending indices of `slice`.
      sequence: `iterable` object to assign to the slice.

    Returns:
      `self`, to permit chaining through direct calls to `plist.__setslice__`.
    """
    if self.__pepth__ != 0:
      if '__warned__' not in plist.__setslice__.__dict__:
        qj('Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!\n'
           'Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.\n'
           'This avoids the broken code path in the python compiler.', 'WARNING!')
        plist.__setslice__.__dict__['__warned__'] = True
      return plist.__getattr__(self, '__setslice__')(i, j, sequence)
    try:
      list.__setslice__(self, i, j, sequence)
    except Exception:
      plist.__setitem__(self, slice(i, j), sequence)
    return self

  ##############################################################################
  # __del*__
  ##############################################################################
  def __delattr__(self, name):
    """Recursively attempt to get the attribute `name`.

    TODO

    Args:
      name: Name of attribute to delete.

    Returns:
      self, in order to allow chaining through `pl.__delattr__(name).foo`.
    """
    if self.__pepth__ != 0:
      return plist.__getattr__(self, '__delattr__')(name)
    for x in self:
      x.__delattr__(name)
    return self

  def __delitem__(self, key):
    """Deletes items of self using a variety of potential indexing styles.

    TODO

    Args:
      key: The key to index by.
           The key can be applied to self directly as:
             A list of ints: Deletes from self using those ints as indices.
             A slice: Deletes from self based on the slice.
             An int: Deletes the value at that index.
           The key can be applied to elements of self individually:
             A generic list: Deletes from the elements of self using the
                             elements of the key in order on the elements of
                             self.
             A tuple when the elements of self can be indexed by tuple:
                      Deletes from the elements of self by applying that tuple
                      to each element of self.
             A tuple, otherwise:
                      Deletes from the elements of self where each element gets
                      each element in the key tuple deleted. E.g.,
                      `del foo[('bar', 'baz')]` deletes all `'bar'` and `'baz'`
                      keys from each element of foo.
             Anything else: Deletes the key from each of its elements.

    Returns:
      self, in order to allow chaining through `pl.__delitem__(key).foo`.

    Raises:
      TypeError: If the key fails to be applied directly to self and fails to be
                 applied to its elements individually.
    """
    if self.__pepth__ != 0:
      return plist.__getattr__(self, '__delitem__')(key)
    try:
      if (isinstance(key, list)
          and plist(key).all(isinstance, int)):
        for k in sorted(key, reverse=True):
          operator.__delitem__(self, k)
      else:
        # Handles slices and ints. Other key types will fail.
        list.__delitem__(self, key)
    except Exception as first_exception:
      try:
        if isinstance(key, list):
          for i, k in enumerate(key):
            operator.__delitem__(self[i], k)
        elif isinstance(key, tuple):
          try:
            for x in self:
              operator.__delitem__(x, key)
          except Exception:
            for x in self:
              for k in key:
                operator.__delitem__(x, k)
        else:
          for x in self:
            operator.__delitem__(x, key)
      except Exception as second_exception:
        raise TypeError('Failed to apply index to self or elements.\nself exception: %s\nelements exception: %s' % (str(first_exception), str(second_exception)))

    # Allow chaining of set ops when using apply('__delitem__', k) and apply(operators.__delitem__, k)
    return self

  def __delslice__(self, i, j):
    """Delegates to `__delitem__` whenever possible. For compatibility with python 2.7.

    Avoid using `__delslice__` whenever possible in python 2.7, as the bytecode compiler
    assumes that the slice is for the given object on the stack, and modifies negative
    indices relative to that object's length. In `plist`s and other dynamic apis like
    `numpy`, that assumption can cause undetectable and unrecoverable errors.

    To avoid the errors caused by this api in python 2.7, simply use three argument
    slices instead of two; e.g., `plist[::1]`.

    Examples:

    The following examples are safe uses of slicing with `plist`s:
    ```python
    pl = plist['abc', 'def', 'ghi']
    del pl[:2:1]
    assert (pl.aslist() ==
            ['ghi'])

    # Change slices of the lists:
    pl = plist['abc', 'def', 'ghi']
    # Turn strings into mutable lists:
    pl = pl.apply(list)
    del pl._[:2:1]
    # Turn lists back into strings:
    pl = pl.apply(''.join)
    assert (pl.aslist() ==
            ['c', 'f', 'i'])
    ```

    The following example will log a warning -- even though it appears to work, the
    underlying bytecode is incorrect:
    ```python
    pl = plist['abc', 'def', 'ghi']
    # Turn strings into mutable lists:
    pl = pl.apply(list)
    del pl._[:2]
    # Turn lists back into strings:
    pl = pl.apply(''.join)
    assert (pl.aslist() ==
            ['c', 'f', 'i'])
    # Logs:
    #   qj: <pstar> __delslice__: WARNING! <1711>: (multiline log follows)
    #   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
    #   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
    #   This avoids the broken code path in the python compiler.
    ```

    Args:
      i, j: Beginning and ending indices of `slice`.
      sequence: `iterable` object to assign to the slice.

    Returns:
      `self`, to permit chaining through direct calls to `plist.__setslice__`.
    """
    if self.__pepth__ != 0:
      if '__warned__' not in plist.__delslice__.__dict__:
        qj('Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!\n'
           'Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.\n'
           'This avoids the broken code path in the python compiler.', 'WARNING!')
        plist.__delslice__.__dict__['__warned__'] = True
      return plist.__getattr__(self, '__delslice__')(i, j)
    try:
      list.__delslice__(self, i, j)
    except Exception:
      plist.__delitem__(self, slice(i, j))
    return self

  ##############################################################################
  # __call__
  ##############################################################################
  def __call__(self, *args, **kwargs):
    """Call each element of self, possibly recusively.

    Any arguments passed to `__call__` that are `plist`s and have the same
    length as `self` will be passed one-at-a-time to the each of the `callable`s
    in `self`. Otherwise, arguments are passed in unmodified.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])

    # A plist of callables, one for each pdict:
    foos_peys = foos.peys
    assert (foos_peys.all(callable))

    # The actual call to plist.__call__ (separated out for demonstration):
    assert (foos_peys().aslist() ==
            [['bar', 'foo'], ['bar', 'foo'], ['bar', 'foo']])

    # Of course, you would normally do the above like this, which is the same:
    assert (foos.peys().aslist() ==
            [['bar', 'foo'], ['bar', 'foo'], ['bar', 'foo']])

    by_bar = foos.bar.groupby()

    # There's rarely any need to pass pepth, as the call gets routed to the
    # correct object by default in almost all situations, even with grouped
    # plists:
    assert (by_bar.peys().aslist() ==
            [[['bar', 'foo'], ['bar', 'foo']], [['bar', 'foo']]])
    ```

    All argument calling conventions are possible:
    ```python
    pl = plist['foo {}', 'bar {}', 'baz {}']

    # Basic positional argument passing:
    assert (pl.format(0).aslist() ==
            ['foo 0', 'bar 0', 'baz 0'])

    # Passing a plist in a positional argument:
    assert (pl.format(pl._[:3:1]).aslist() ==
            ['foo foo', 'bar bar', 'baz baz'])

    # Basic keyword argument passing:
    pl = pl.replace('{}', '{foo}')
    assert (pl.format(foo=0).aslist() ==
            ['foo 0', 'bar 0', 'baz 0'])

    # Passing a plist as a keyword argument:
    assert (pl.format(foo=pl._[:3:1]).aslist() ==
            ['foo foo', 'bar bar', 'baz baz'])
    ```

    They work the same way on grouped plists:
    ```python
    pl = plist['foo {}', 'bar {}', 'baz {}']
    by = pl._[0].groupby()  # Group by first character.
    assert (by.aslist() ==
            [['foo {}'], ['bar {}', 'baz {}']])

    # Basic positional argument passing:
    assert (by.format(0).aslist() ==
            [['foo 0'], ['bar 0', 'baz 0']])

    # Passing a plist in a positional argument:
    assert (by.format(by._[:3:1]).aslist() ==
            [['foo foo'], ['bar bar', 'baz baz']])

    # Basic keyword argument passing:
    by = by.replace('{}', '{foo}')
    assert (by.format(foo=0).aslist() ==
            [['foo 0'], ['bar 0', 'baz 0']])

    # Passing a plist as a keyword argument:
    assert (by.format(foo=by._[:3:1]).aslist() ==
            [['foo foo'], ['bar bar', 'baz baz']])
    ```

    Args:
      *args: Arguments to pass to elements of `self`.
      **kwargs: Keyword arguments to pass to elements of `self`, after extracting:
      pepth: Integer (default `0`). If greater than `0`, calls occur at that
             depth in the `plist`. Equivalent to appending '_'s at the end of the
             name of the attribute (see `plist.__getattribute__`). If less than
             `0`, calls occur as deep in the `plist` as possible. Equivalent to
             calling `plist._` before calling the attribute.
      psplit: Integer (default `0`). If greater than `0`, calls to elements of
              `self` are applied in parallel. If `psplit` is `1`, the number of
              parallel executions is equal to the length of `self`.
              Otherwise, `psplit` is the number of parallel executions.
      call_pepth: *Private -- do not pass.* Internal state variable for tracking
                  how deep the call stack is in `plist` code, for use with
                  internal methods that need access to the original caller's
                  stack frame.

    Returns:
      New `plist` resulting from calling element of `self`.
    """
    pepth = kwargs.pop('pepth', self.__pepth__)
    self.__pepth__ = 0
    call_pepth = kwargs.pop('call_pepth', 0)
    psplit = kwargs.pop('psplit', 0)

    args = [_ensure_len(len(self), a, strict=True) for a in args]
    kwargs = {
        k: _ensure_len(len(self), v, strict=True) for k, v in kwargs.items()
    }
    if pepth != 0:
      try:
        return plist([x(pepth=pepth - 1,
                        call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA,
                        *[a[i] for a in args],
                        **{k: v[i] for k, v in kwargs.items()})
                      for i, x in enumerate(self)],
                     root=self.__root__)
      except Exception as e:
        if pepth > 0:
          raise e

    if psplit > 0:
      pool = _get_thread_pool(psplit, len(self))

      call_args = [pdict(x=x, i=i) for i, x in enumerate(self)]
      map_func = lambda ca: ca.x(*[a[ca.i] for a in args],
                                 **{k: v[ca.i] for k, v in kwargs.items()})
      return plist(pool.map(map_func, call_args, chunksize=_get_thread_chunksize(psplit, len(self))), root=self.__root__)
    return plist([x(*[a[i] for a in args],
                    **{k: v[i] for k, v in kwargs.items()})
                  for i, x in enumerate(self)],
                 root=self.__root__)

  ##############################################################################
  # __contains__
  ##############################################################################
  def __contains__(self, other):
    """Implements the `in` operator to avoid inappropriate use of `plist` comparators.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (2 in foos.foo)
    assert (dict(foo=0, bar=0) in foos)

    by_bar = foos.bar.groupby()
    assert (2 in by_bar.foo)
    assert (dict(foo=0, bar=0) in by_bar)
    ```

    Returns:
      `bool` value indicating whether `other` was found in `self`.
    """
    if self is other:
      return False
    found = False
    try:
      found = self.any(plist.__contains__, other)
    except Exception as e:
      pass
    return (found
            or any([x is other
                    or (not isinstance(x, plist)
                        and not isinstance(other, plist)
                        and x == other) for x in self]))

  ##############################################################################
  # Comparison operators -- ALL PERFORM FILTERING!
  ##############################################################################
  __cmp__ = _build_comparator(
      operator.__eq__,
      operator.__or__,
      lambda self, return_inds: (
          self.lfill(pepth=-1)
          if return_inds else self),
      False)
  __eq__ = __cmp__

  __ne__ = _build_comparator(
      operator.__ne__,
      operator.__and__,
      lambda self, return_inds: ([] if return_inds else plist()),
      True)

  __gt__ = _build_comparator(
      operator.__gt__,
      operator.__and__,
      lambda self, return_inds: ([] if return_inds else plist()),
      True)

  __ge__ = _build_comparator(
      operator.__ge__,
      operator.__and__,
      lambda self, return_inds: (
          self.lfill(pepth=-1)
          if return_inds else self),
      True)

  __lt__ = _build_comparator(
      operator.__lt__,
      operator.__and__,
      lambda self, return_inds: ([] if return_inds else plist()),
      True)

  __le__ = _build_comparator(
      operator.__le__,
      operator.__and__,
      lambda self, return_inds: (
          self.lfill(pepth=-1)
          if return_inds else self),
      True)

  ##############################################################################
  # Logical operators -- ALL PERFORM SET OPERATIONS!
  ##############################################################################
  __and__ = _build_logical_op(operator.__and__)
  __rand__ = _build_binary_rop(operator.__and__)
  __iand__ = _build_binary_op(operator.__iand__)

  __or__ = _build_logical_op(operator.__or__)
  __ror__ = _build_binary_rop(operator.__or__)
  __ior__ = _build_binary_op(operator.__ior__)

  __xor__ = _build_logical_op(operator.__xor__)
  __rxor__ = _build_binary_rop(operator.__xor__)
  __ixor__ = _build_binary_op(operator.__ixor__)

  ##############################################################################
  # Binary operators
  ##############################################################################
  __add__, __radd__, __iadd__ = _build_binary_ops(operator.__add__, operator.__iadd__)
  __sub__, __rsub__, __isub__ = _build_binary_ops(operator.__sub__, operator.__isub__)
  __mul__, __rmul__, __imul__ = _build_binary_ops(operator.__mul__, operator.__imul__)
  __truediv__, __rtruediv__, __itruediv__ = _build_binary_ops(operator.__truediv__, operator.__itruediv__)

  if sys.version_info[0] < 3:
    __div__, __rdiv__, __idiv__ = _build_binary_ops(operator.__div__, operator.__idiv__)

  __pow__, __rpow__, __ipow__ = _build_binary_ops(operator.__pow__, operator.__ipow__)

  __mod__, __rmod__, __imod__ = _build_binary_ops(operator.__mod__, operator.__imod__)

  __divmod__ = _build_binary_op(divmod)
  __rdivmod__ = _build_binary_rop(divmod)

  __floordiv__, __rfloordiv__, __ifloordiv__ = _build_binary_ops(operator.__floordiv__, operator.__ifloordiv__)

  __lshift__, __rlshift__, __ilshift__ = _build_binary_ops(operator.__lshift__, operator.__ilshift__)
  __rshift__, __rrshift__, __irshift__ = _build_binary_ops(operator.__rshift__, operator.__irshift__)

  ##############################################################################
  # Unary operators
  ##############################################################################
  __neg__ = _build_unary_op(operator.__neg__)

  __pos__ = _build_unary_op(operator.__pos__)

  __abs__ = _build_unary_op(abs)

  __invert__ = _build_unary_op(operator.__invert__)

  __complex__ = _build_unary_op(complex)

  __int__ = _build_unary_op(int)

  if sys.version_info[0] < 3:
    __long__ = _build_unary_op(long)

  __float__ = _build_unary_op(float)

  __oct__ = _build_unary_op(oct)

  __hex__ = _build_unary_op(hex)

  ##############################################################################
  # Ensure plists can't be hashed.
  ##############################################################################
  __hash__ = None

  # Nope.  Crashes when trying to index by plists of lists of ints.
  # def __index__(self):
  #   return plist([x.__index__() for x in self], root=self.__root__)

  ##############################################################################
  # Allow plist use as context managers.
  ##############################################################################
  def __enter__(self):
    """Allow the use of plists in `with` statements.

    Examples:
    ```python
    import glob, os
    path = os.path.dirname(__file__)
    filenames = plist(glob.glob(os.path.join(path, '*.py')))
    with filenames.apply(open, 'r') as f:
      texts = f.read()
    assert (len(texts) >= 1)
    assert (len(texts.all(isinstance, str)) >= 1)
    ```

    Returns:
      `plist` of results of calling `__enter__` on each element of `self`.
    """
    return plist([x.__enter__() for x in self], root=self.__root__)

  def __exit__(self, exc_type, exc_value, traceback):
    """Allow the use of plists in `with` statements.

    See `plist.__enter__`.

    Returns:
      `plist` of results of calling `__exit__` on each element of `self`.
    """
    return plist([x.__exit__(exc_type, exc_value, traceback) for x in self], root=self.__root__).all(bool)

  ##############################################################################
  ##############################################################################
  ##############################################################################
  # Public methods.
  ##############################################################################
  ##############################################################################
  ##############################################################################

  def _(self):
    """Causes the next call to `self` to be performed as deep as possible in the `plist`.

    This is a convenience method primarily for easy subscripting of the values of
    a `plist`.

    Examples:
    ```python
    pl = plist([np.arange(10) for _ in range(3)])
    assert (pl._[2].aslist() ==
            [2, 2, 2])
    import operator as op
    assert (pl._[2:4:1].apply(op.eq,
                              [np.array([2, 3]), np.array([2, 3]), np.array([2, 3])])
                       .apply(np.all).aslist() ==
            [True, True, True])
    ```

    It can be used to call any method on the values of a `plist` as well:
    ```python
    pl = plist([['foo'], ['bar']])
    pl._.append('baz')
    assert (pl.apply(type).aslist() ==
            [list, list])
    assert (pl.aslist() ==
            [['foo', 'baz'], ['bar', 'baz']])
    ```

    Returns:
      `self`, but in a state such that the next access to a property or method of
      `self` occurs at the maximum depth.
    """
    self.__pepth__ = -1
    return self

  ##############################################################################
  # __root__ pointer management.
  ##############################################################################
  def root(self):
    """Returns the root of the `plist`.

    Examples:

    When a `plist` is created, by default its root is `self`:
    ```python
    pl = plist([1, 2, 3])
    assert (pl.root() is pl)
    ```

    Subsequent calls to the `plist` will return new `plist`s, but most of those
    calls will retain the original root:
    ```python
    pl2 = pl + 3
    assert (pl2.aslist() ==
            [4, 5, 6])
    assert (pl2.root() is pl)
    assert (pl2.pstr().root() is pl)
    ```

    Some methods create a new root `plist` in order to keep the values and the root
    syncronized:
    ```python
    assert (pl2[0:2].aslist() ==
            [4, 5])
    assert (pl2[0:2].root().aslist() ==
            [1, 2])
    assert (pl2.sortby(reverse=True).aslist() ==
            [6, 5, 4])
    assert (pl2.sortby(reverse=True).root().aslist() ==
            [3, 2, 1])
    ```

    `plist` filtering also always returns the root, in order to make the filter easily chainable:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    filtered = foo.bar == 0
    assert (filtered.aslist() ==
            [dict(foo=0, bar=0), dict(foo=2, bar=0)])
    assert (filtered.root() is filtered)
    (foo.bar == 0).baz = 6
    (foo.bar == 1).baz = foo.foo * 2
    assert (foo.aslist() ==
            [dict(foo=0, bar=0, baz=6), dict(foo=1, bar=1, baz=2), dict(foo=2, bar=0, baz=6)])
    ```

    Grouping also always returns the root:
    ```python
    by_bar = foo.bar.groupby()
    assert (by_bar.aslist() ==
            [[{'bar': 0, 'baz': 6, 'foo': 0}, {'bar': 0, 'baz': 6, 'foo': 2}],
             [{'bar': 1, 'baz': [0, 2, 4], 'foo': 1}]])
    assert (by_bar.aslist() == by_bar.root().aslist())
    ```

    Returns:
      The root `plist` of `self`.
    """
    return self.__root__

  def uproot(self):
    """Sets the root to `self` so future `root()` calls return this `plist`.

    Examples:

    In some cases it is better reset the root. For example, after applying
    a number of operations to a `plist` to get the data into the desired form,
    resetting the root to `self` often makes sense, as future filtering
    should not return the original data:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foo.bar == 0).baz = 6
    (foo.bar == 1).baz = foo.foo * 2
    floo = foo.rekey(dict(foo='floo'))
    assert (floo.root() is foo)
    assert (floo.peys()[0].aslist() ==
            ['bar', 'baz', 'floo'])
    assert ((floo.floo < 2).aslist() ==
            [dict(foo=0, bar=0, baz=6), dict(foo=1, bar=1, baz=2)])
    floo = floo.uproot()
    assert ((floo.floo < 2).aslist() ==
            [dict(floo=0, bar=0, baz=6), dict(floo=1, bar=1, baz=2)])
    ```

    See `plist.root` for more details.

    Returns:
      `self`.
    """
    self.__root__ = self
    return self

  ##############################################################################
  # Conversion methods.
  ##############################################################################
  def copy(self):
    """Copy `self` to new `plist`. Performs a shallow copy.

    `self.root()` is copied as well and used to root the copy if
    `self.root() is not self`.
    If `self.root() is self`, the root is not maintained.

    Examples:
    ```python
    pl1 = plist[1, 2, 3]
    pl2 = pl1.copy()
    assert (pl1 is not pl2)
    assert (pl1.root() is pl1 and pl2.root() is pl2)

    pl3 = pl2 + 1
    pl4 = pl3.copy()
    assert (pl4.root().aslist() == pl3.root().aslist())
    assert (pl4.root() is not pl3.root())
    assert (pl4.root().aslist() == pl2.aslist())
    assert (pl4.root() is not pl2)
    ```

    Returns:
      Copy of `self` with `self.root()` handled appropriately.
    """
    if self.__root__ is self:
      return plist(self)
    return plist(self, root=self.__root__.copy())

  def aslist(self):
    """Recursively convert all nested `plist`s from `self` to `list`s, inclusive.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foo.bar.groupby()
    assert (by_bar.apply(type).aslist() == [plist, plist])
    assert ([type(x) for x in by_bar.aslist()] == [list, list])
    ```

    Returns:
      `list` with the same structure and contents as `self`.
    """
    try:
      return [x.aslist() for x in self]
    except Exception:
      pass
    return [x for x in self]

  def astuple(self):
    """Recursively convert all nested `plist`s from `self` to `tuple`s, inclusive.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foo.bar.groupby()
    assert (by_bar.apply(type).aslist() == [plist, plist])
    assert ([type(x) for x in by_bar.astuple()] == [tuple, tuple])
    ```

    Returns:
      `tuple` with the same structure and contents as `self`.
    """
    try:
      return tuple([x.astuple() for x in self])
    except Exception:
      pass
    return tuple([x for x in self])

  def aspset(self):
    """Recursively convert all nested `plist`s from `self` to `pset`s, inclusive.

    All values must be hashable for the conversion to succeed.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.bar.aspset() == pset([0, 1]))
    by_bar = foo.bar.groupby()
    assert (by_bar.bar.apply(type).aslist() == [plist, plist])
    assert ([type(x) for x in by_bar.bar.aspset()] == [pset, pset])
    ```

    Returns:
      `pset` with the same structure and contents as `self`.
    """
    try:
      return pset([x.aspset() for x in self])
    except Exception:
      pass
    return pset([x for x in self])

  def aspdict(self):
    """Convert `self` to a `pdict` if there is a natural mapping of keys to values in `self`.

    Recursively creates a `pdict` from `self`. Experimental, likely to change.

    Examples:
    ```python
    pl = plist['foo', 'bar', 'baz']
    assert (pl.pdict() ==
            dict(foo='foo', bar='bar', baz='baz'))
    assert (pl.replace('a', '').replace('o', '').pdict() ==
            dict(foo='f', bar='br', baz='bz'))

    foos = plist([pdict(foo=0, bar=0, baz=3), pdict(foo=1, bar=1, baz=2), pdict(foo=2, bar=0, baz=1)])
    by_bar = foos.bar.groupby()
    assert (by_bar.bar.ungroup().puniq().zip(by_bar).aspdict() ==
            {0: [{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 1, 'foo': 2}],
             1: [{'bar': 1, 'baz': 2, 'foo': 1}]})
    assert ([type(x) for x in by_bar.astuple()] == [tuple, tuple])
    ```

    Returns:
      New `pdict` based on the contents of `self`.
    """
    pd = self.pdict()
    try:
      pd.update({k: v.aspdict() for k, v in pd.pitems()})
    except Exception:
      pass
    return pd

  if np is None:
    def np(self, *args, **kwargs):
      """If `numpy` were installed on your system, `plist.np()` would convert your `plist` to a `numpy.array`.

      Please install `numpy`:
      ```bash
      pip install numpy
      ```

      Raises:
        NotImplementedError: We can't give you `numpy.array`s if you don't give us `numpy`.
      """
      raise NotImplementedError('numpy is unavailable on your system. Please install numpy before calling plist.np().')
  else:
    def np(self, *args, **kwargs):
      """Converts the elements of `self` to `numpy.array`s, forwarding passed args.

      Examples:
      ```python
      foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
      (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
      (foos.bar == 1).baz = 6
      foos.bin = -1
      assert (foos.aslist() ==
              [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
               {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 1},
               {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
               {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 3},
               {'bar': 0, 'baz': 7, 'bin': -1, 'foo': 4}])

      assert (foos.foo.join().np().sum().aslist() ==
              [10])

      by_bar = foos.bar.sortby(reverse=True).groupby()
      baz = by_bar.baz
      # Filters for the max per group, which includes the two-way tie in the first group.
      (baz == baz.np().max()).bin = 13

      assert (by_bar.aslist() ==
              [[{'bar': 1, 'baz': 6, 'bin': 13, 'foo': 1},
                {'bar': 1, 'baz': 6, 'bin': 13, 'foo': 3}],
               [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
                {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
                {'bar': 0, 'baz': 7, 'bin': 13, 'foo': 4}]])

      assert ((by_bar.foo.np() * by_bar.baz.np() - by_bar.bin.np()).sum().aslist() ==
              [-2, 27])
      ```

      Args:
        *args: Positional arguments passed to `np.array`.
        **kwargs: Keyword arguments passed to `np.array`.

      Returns:
        New `plist` with values from `self` converted to `np.array`s.
      """
      return plist([np.array(x, *args, **kwargs) for x in self], root=self.__root__)

  if pd is None:
    def pd(self, *args, **kwargs):
      """If `pandas` were installed on your system, `plist.pd()` would convert your `plist` to a `pandas.DataFrame`.

      Please install `pandas`:
      ```bash
      pip install pandas
      ```

      Raises:
        NotImplementedError: We can't give you `panda.DataFrame`s if you don't give us `pandas`.
      """
      raise NotImplementedError('pandas is unavailable on your system. Please install pandas before calling plist.pd().')
  else:
    def pd(self, *args, **kwargs):
      r"""Converts `self` into a `pandas.DataFrame`, forwarding passed args.

      Examples:
      ```python
      foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
      (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
      (foos.bar == 1).baz = 6
      foos.bin = -1

      assert (foos.aslist() ==
              [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
               {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 1},
               {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
               {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 3},
               {'bar': 0, 'baz': 7, 'bin': -1, 'foo': 4}])

      by_bar = foos.bar.sortby(reverse=True).groupby()
      baz = by_bar.baz
      (baz == baz.np().max()).bin = 13

      assert (by_bar.aslist() ==
              [[{'bar': 1, 'baz': 6, 'bin': 13, 'foo': 1},
                {'bar': 1, 'baz': 6, 'bin': 13, 'foo': 3}],
               [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
                {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
                {'bar': 0, 'baz': 7, 'bin': 13, 'foo': 4}]])

      assert (str(foos.pd()) ==
              '   bar  baz  bin  foo\n'
              '0    1    6   13    1\n'
              '1    1    6   13    3\n'
              '2    0    3   -1    0\n'
              '3    0    5   -1    2\n'
              '4    0    7   13    4')

      assert (str(foos.pd(index='foo')) ==
              '     bar  baz  bin\n'
              'foo               \n'
              '1      1    6   13\n'
              '3      1    6   13\n'
              '0      0    3   -1\n'
              '2      0    5   -1\n'
              '4      0    7   13')

      assert (by_bar.pd_().pstr().aslist() ==
              ['   bar  baz  bin  foo\n'
               '0    1    6   13    1\n'
               '1    1    6   13    3',

               '   bar  baz  bin  foo\n'
               '0    0    3   -1    0\n'
               '1    0    5   -1    2\n'
               '2    0    7   13    4'])
      ```
      Note the use of `pd_()` on the grouped `plist`. This allows you to get a separate `pandas.DataFrame` for
      each group in your `plist`, and then do normal `DataFrame` manipulations with them individually.
      If you want a `pandas.GroupBy` object, you should convert the `plist` to a `DataFrame` first, and then
      call `DataFrame.groupby`. Also see `plist.remix` for alternative ways of converting `plist`s to
      `DataFrame`s.

      Args:
        *args: Positional arguments passed to `pandas.DataFrame.from_records`.
        **kwargs: Keyword arguments passed to `pandas.DataFrame.from_records`.

      Returns:
        A `pandas.DataFrame` object constructed from `self`.
      """
      return pd.DataFrame.from_records(self.aslist(), *args, **kwargs)

  def pdict(self, *args, **kwargs):
    """Convert `self` to a `pdict` if there is a natural mapping of keys to values in `self`.

    Attempts to treat the contents of `self` as key-value pairs in order to create the `pdict`.
    If that fails, checks if `self.root()` is a `plist` of `KeyValue` tuples. If so, uses
    `self.root().key` for the keys, and the values in `self` for the values. Otherwise,
    attempts to create a `pdict` pairing values from `self.root()` with values from `self`.

    Examples:
    ```python
    pl = plist['foo', 'bar', 'baz']
    assert (pl.pdict() ==
            dict(foo='foo', bar='bar', baz='baz'))
    assert (pl.replace('a', '').replace('o', '').pdict() ==
            dict(foo='f', bar='br', baz='bz'))

    pd = pdict(foo=1, bar=2, floo=0)
    assert (pd.pitems().pdict() == pd)
    assert (pd.palues().pdict() == pd)
    assert ((pd.palues() + 2).pdict() ==
            dict(foo=3, bar=4, floo=2))
    assert (pd.peys()._[0].pdict(),
            pdict(foo='f', bar='b', floo='f'))

    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.pstr().zip(foos.bar).uproot().pdict() ==
            {'0': 0, '1': 1, '2': 0})

    assert (plist[('foo', 1), ('foo', 2)].pdict() ==
            dict(foo=2))
    ```

    Returns:
      New `pdict` based on the contents of `self`.
    """
    try:
      return pdict({k: v for k, v in self}).update(*args, **kwargs)
    except Exception:
      pass
    if self.__root__.all(isinstance, KeyValue):
      return pdict({k: v for k, v in zip(self.__root__.key, self)}).update(*args, **kwargs)
    return pdict({k: v for k, v in zip(self.__root__, self)}).update(*args, **kwargs)

  def pset(self):
    """Converts the elements of self into pset objects.

    Useful for creating `set`s from grouped `plist`s.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.pitems().pset().aslist() ==
            [{('foo', 0), ('bar', 0)}, {('foo', 1), ('bar', 1)}, {('foo', 2), ('bar', 0)}])

    by_bar = foos.bar.groupby()
    assert (by_bar.foo.pset().aslist() ==
            [{0, 2}, {1}])
    ```

    Returns:
      New `plist` of `pset`s for each value in `self`.
    """
    return plist([pset(x) for x in self], root=self.__root__)

  def pstr(self):
    """Returns a plist with leaf elements converted to strings.

    Calls `str` on each leaf element of self.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.pstr().aslist() ==
            ['0', '1', '2'])

    by_bar = foos.bar.groupby()
    assert (by_bar.foo.pstr().aslist() ==
            [['0', '2'], ['1']])
    ```

    Note that string concatenation works naturally with `plist`s, so it is easy to build
    up a desired string using `plist.pstr`:
    ```python
    assert (('foo: ' + by_bar.foo.pstr() + ', bar: ' + by_bar.bar.pstr()).aslist() ==
            [['foo: 0, bar: 0', 'foo: 2, bar: 0'], ['foo: 1, bar: 1']])
    ```

    If you want the string representation of a layer of a grouped `plist`, instead use
    `plist.apply(str)` at the desired depth:
    ```python
    assert (by_bar.foo.apply(str).aslist() ==
            ['[0, 2]', '[1]'])
    ```

    Returns:
      `plist` of strings.
    """
    try:
      return plist([x.pstr() for x in self], root=self.__root__)
    except Exception:
      return plist([str(x) for x in self], root=self.__root__)

  ##############################################################################
  # Matplotlib pyplot convenience methods.
  ##############################################################################
  if plt is None:
    def plt(self, *args, **kwargs):
      """If `matplotlib.pyplot` were installed on your system, `plist.plt()` would make your use of `pyplot` easier.

      Please install `matplotlib.pyplot`:
      ```bash
      pip install matplotlib
      ```

      Raises:
        NotImplementedError: We can't make `pyplot` easier to use if you don't give us `pyplot`.
      """
      raise NotImplementedError('matplotlib.pyplot is unavailable on your system. Please install matplotlib.pyplot before calling plist.plt().')
  else:
    def plt(self, **kwargs):
      """Convenience method for managing `matplotlib.pyplot` state within a `plist` chain.

      `plt()` serves two purposes:
      1. It returns a delegation object that allows calling `pyplot` functions without having to call `apply` -- e.g.,
         `plist.plt().plot()` instead of `plist.apply(plt.plot)`.
      1. It allows calling of multiple `pyplot` functions in a single call just by passing `**kwargs`. This
         makes it easier to set up plotting contexts and to control when plots are shown, without adding
         lots of one-line `plt` calls before and after the data processing and plotting code.

      Neither of these use cases provides anything that can't be done directly with normal calls to `plt`
      functions and `plist.apply`. This method is just to make your life easier if you do a lot of
      plotting.

      When passing `kwargs` to `plt()`, they are executed in alphabetical order. If that is inappropriate,
      (e.g., when creating a figure and setting other parameters), you can break up the call into two or
      more `plt()` calls to enforce any desired ordering, but you should probably just do that kind of
      complicated setup outside of the `plist` context.

      Examples:
      ```python
      foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
      (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
      (foos.bar == 1).baz = 6

      foos.foo.plt().scatter(foos.bar).plt(show=None)
      # Equivlent to:
      foos.foo.apply(plt.scatter, foos.bar)
      plt.show()

      by_bar = foos.bar.groupby()
      by_bar.foo.plt().plot().plt(show=None)
      # Equivlent to:
      by_bar.foo.apply(plt.plot)
      plt.show()

      # Create a figure of size 12x8, set the x and y limits, add x and y axis labels,
      # draw a scatter plot with custom colors and labels per group, add the legend, and show the figure.
      by_bar.foo.plt(
          figure=dict(figsize=(12, 8)), xlim=(-1, 5), ylim=(-1, 7), xlabel='foo', ylabel='baz'
      ).scatter(
          by_bar.baz, c=plist['r', 'g'], label='bar: ' + by_bar.bar.puniq().ungroup().pstr()
      ).plt(legend=dict(loc=0), show=None)

      # Equivalent to:
      plt.figure(figsize=(12, 8))
      plt.xlabel('foo')
      plt.xlim((-1, 5))
      plt.ylabel('baz')
      plt.ylim((-1, 7))
      by_bar.foo.apply(plt.scatter, by_bar.baz, c=plist['r', 'g'], label='bar: ' + by_bar.bar.puniq().ungroup().pstr())
      plt.legend(loc=0)
      plt.show()
      ```

      Args:
        **kwargs: Key/value pairs where the key is a function name on `plt`, and the value is the arguments
                  to call that function with, or `None` for an empty call.

      Returns:
        Delegation object that can call `pyplot` functions like `plt.plot`, as well as accessing whatever
        properties are available to elements of `self`.
      """
      def call_plt_fn(attr, args):
        attr = getattr(plt, attr)
        if args is None:
          attr()
        elif isinstance(args, list):
          if isinstance(args[-1], dict):
            attr(*args[:-1], **args[-1])
          else:
            attr(*args)
        elif isinstance(args, dict):
          attr(**args)
        else:
          attr(args)

      kwargs = pdict(kwargs)
      kwargs.pitems().apply(call_plt_fn, psplat=True)

      class Plt(object):
        """Wrapper class for calling `plt` functions in a `plist` context.

        Permits dynamic access to `plt` functions while maintaining the current
        `plist` values.
        """
        def __init__(self, first_arg):
          self.first_arg = first_arg
          self.last_plt = None

        def __getattr__(self, name):
          first_arg = self.first_arg
          if isinstance(first_arg, Plt):
            first_arg = first_arg.first_arg
          try:
            attr = getattr(plt, name)
            def call_plt_fn(*a, **kw):
              self.last_plt = attr(first_arg, *a, **kw)
              return self
            return call_plt_fn
          except Exception:
            return getattr(first_arg, name)

      return plist([Plt(x) for x in self], root=self.__root__)


  ##############################################################################
  # Shortcutting boolean test methods.
  ##############################################################################
  def all(self, *args, **kwargs):
    """Returns `self` if `args[0]` evaluates to `True` for all elements of `self`.

    Shortcuts if `args[0]` ever evaluates to `False`.
    If `args` are not passed, the function evaluated is `bool`.

    Useful as an implicit `if` condition in chaining, but can be used explicitly
    in `if` statements as well.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.all(isinstance, pdict).aslist() ==
            [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.all(lambda x: x > 0).aslist() == [])
    ```

    `all` does not recurse into grouped `plist`s, so you must specify the
    desired level of evaluation:
    ```python
    by_bar = foos.bar.groupby()
    assert (by_bar.foo.all_(lambda x: x > 0).aslist() ==
            [[], [1]])
    assert (by_bar.foo.all_(lambda x: x > 0).nonempty().root().aslist() ==
            [[{'bar': 1, 'foo': 1}]])
    ```

    Args:
      *args: Optional. If present, the first entry must be a function to evaluate.
             All other args are passed through to that function. If absent, the
             function is set to `bool`.
      **kwargs: Passed through to the function specified in `*args`.

    Returns:
      `self` or an empty `plist` (which evaluates to `False`).
    """
    if len(args):
      func = args[0]
      args = args[1:]
    else:
      func = bool
    for x in self:
      if not func(x, *args, **kwargs):
        return plist()
    return self

  def any(self, *args, **kwargs):
    """Returns `self` if `args[0]` evaluates to `True` for any elements of `self`.

    Shortcuts if `args[0]` ever evaluates to `True`.
    If `args` are not passed, the function evaluated is `bool`.

    Useful as an implicit `if` condition in chaining, but can be used explicitly
    in `if` statements as well.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.any(isinstance, pdict).aslist() ==
            [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.any(lambda x: x < 0).aslist() == [])
    ```

    `any` does not recurse into grouped `plist`s, so you must specify the
    desired level of evaluation:
    ```python
    by_bar = foos.bar.groupby()
    assert (by_bar.foo.any_(lambda x: x > 1).aslist() ==
            [[0, 2], []])
    assert (by_bar.foo.any_(lambda x: x > 1).nonempty().root().aslist() ==
            [[{'bar': 0, 'foo': 0}, {'bar': 0, 'foo': 2}]])
    ```

    Args:
      *args: Optional. If present, the first entry must be a function to evaluate.
             All other args are passed through to that function. If absent, the
             function is set to `bool`.
      **kwargs: Passed through to the function specified in `*args`.

    Returns:
      `self` or an empty `plist` (which evaluates to `False`).
    """
    if len(args):
      func = args[0]
      args = args[1:]
    else:
      func = bool
    for x in self:
      if func(x, *args, **kwargs):
        return self
    return plist()

  def none(self, *args, **kwargs):
    """Returns `self` if `args[0]` evaluates to `False` for all elements of `self`.

    Shortcuts if `args[0]` ever evaluates to `True`.
    If `args` are not passed, the function evaluated is `bool`.

    Useful as an implicit `if` condition in chaining, but can be used explicitly
    in `if` statements as well.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.none(isinstance, pset).aslist() ==
            [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.none(lambda x: x > 1).aslist() == [])
    ```

    `none` does not recurse into grouped `plist`s, so you must specify the
    desired level of evaluation:
    ```python
    by_bar = foos.bar.groupby()
    assert (by_bar.foo.none_(lambda x: x > 1).aslist() ==
            [[], [1]])
    assert (by_bar.foo.none_(lambda x: x > 1).nonempty().root().aslist() ==
            [[{'bar': 1, 'foo': 1}]])
    ```

    Args:
      *args: Optional. If present, the first entry must be a function to evaluate.
             All other args are passed through to that function. If absent, the
             function is set to `bool`.
      **kwargs: Passed through to the function specified in `*args`.

    Returns:
      `self` or an empty `plist` (which evaluates to `False`).
    """
    if len(args):
      func = args[0]
      args = args[1:]
    else:
      func = bool
    for x in self:
      if func(x, *args, **kwargs):
        return plist()
    return self

  ##############################################################################
  # Equality checking that returns bool instead of plist.
  ##############################################################################
  def pequal(self, other):
    """Shortcutting recursive equality function.

    `pequal` always returns `True` or `False` rather than a plist. This is a
    convenience method for cases when the filtering that happens with `==` is
    undesirable or inconvenient.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foos.pequal(foos) == True)

    zero_bars = foos.bar == 0
    assert (zero_bars.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    assert ((foos == zero_bars).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    assert (foos.pequal(zero_bars) == False)
    ```

    Args:
      other: Object to check equality against.

    Returns:
      True if all elements of self and other are recursively equal.
      False otherwise.
    """
    if not isinstance(other, plist):
      return False
    if len(self) != len(other):
      return False
    try:
      for x, y in zip(self, other):
        if not x.pequal(y):
          return False
    except Exception:
      for x, y in zip(self, other):
        if x != y:
          return False
    return True

  ##############################################################################
  # Function application methods.
  ##############################################################################
  def apply(self, func, *args, **kwargs):
    """Apply an arbitrary function to elements of self, forwarding arguments.

    Any arguments passed to `apply` that are `plist`s and have the same
    length as `self` will be passed one-at-a-time to `func` with each
    element of `self`. Otherwise, arguments are passed in unmodified.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.apply('foo: {}'.format).aslist() ==
            ['foo: 0', 'foo: 1', 'foo: 2'])
    assert (foos.foo.apply('foo: {}, bar: {}'.format, foos.bar).aslist() ==
            ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])
    assert (foos.foo.apply('foo: {}, bar: {bar}'.format, bar=foos.bar).aslist() ==
            ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])

    # The same as above, but in parallel:
    assert (foos.foo.apply('foo: {}, bar: {}'.format, foos.bar, psplit=1).aslist() ==
            ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])

    by_bar = foos.bar.groupby()
    assert (by_bar.foo.apply('bar: {bar} => {}'.format, bar=foos.bar.puniq()).aslist() ==
            ['bar: 0 => [0, 2]', 'bar: 1 => [1]'])
    assert (by_bar.foo.apply_('bar: {bar} => {}'.format, bar=by_bar.bar).aslist() ==
            [['bar: 0 => 0', 'bar: 0 => 2'], ['bar: 1 => 1']])
    ```

    Using `paslist` and `psplat`:
    ```python
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.groupby().baz.groupby()

    by_bar_baz_apply_paslist = by_bar_baz.foo.apply(
        lambda x, *a, **kw: {'{x}: {a} ({kw})'.format(x=x, a=a, kw=kw)}, by_bar_baz.baz, bar=by_bar_baz.bar, paslist=True)
    by_bar_baz_apply_paslist_psplat = by_bar_baz.foo.apply(
        lambda *a, **kw: {'{a} ({kw})'.format(a=a, kw=kw)}, by_bar_baz.baz, bar=by_bar_baz.bar, paslist=True, psplat=True)

    assert (by_bar_baz_apply_paslist.aslist() ==
            [["[[0], [2], [4]]: ([[3], [1], [2]],) ({'bar': [[0], [0], [0]]})"],
             ["[[1, 3]]: ([[6, 6]],) ({'bar': [[1, 1]]})"]])
    assert (by_bar_baz_apply_paslist_psplat.aslist() ==
            [["([0], [2], [4], [[3], [1], [2]]) ({'bar': [[0], [0], [0]]})"],
             ["([1, 3], [[6, 6]]) ({'bar': [[1, 1]]})"]])
    ```

    Args:
      func: `callable`, `list` of `callable`s, or string name of method in `plist`.
      *args: Arguments to pass to `func`.
      **kwargs: Keyword arguments to pass to `func`, after extracting:
      paslist: Boolean (default `False`). If `True`, converts
               elements of `self` to `list` using `plist.aslist()`
               before passing them to `func`, and reconverts the
               result of each call to a `plist`. Note that this does
               not guarantee that the returned `plist` has the same
               shape as `self`, as `plist.aslist()` recursively
               converts all contained `plist`s to `list`s, but `func`
               might return any arbitrary result, so the same
               conversion cannot be inverted automatically.
      psplat: Boolean (default `False`). If `True`, expands the
              arguments provided by `self` with the `*` operator
              (sometimes called the 'splat' operator).
      psplit: Integer (default `0`). If greater than `0`, `func` is
              applied in parallel. If `psplit` is `1`, the number of
              parallel executions is equal to the length of `self`.
              Otherwise, `psplit` is the number of parallel executions.

    Returns:
      `plist` resulting from applying `func` to each element of `self`.
    """
    paslist = kwargs.pop('paslist', False)
    psplat = kwargs.pop('psplat', False)
    psplit = kwargs.pop('psplit', 0)

    args = [_ensure_len(len(self), a, strict=True) for a in args]
    kwargs = {
        k: _ensure_len(len(self), v, strict=True) for k, v in kwargs.items()
    }

    if isinstance(func, str):
      func = plist.__getattribute__(self, func)
      if hasattr(func, '__len__') and len(func) == len(self):
        return plist([func[i](*[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
      else:
        # We should be calling a single function of a plist object.  If that's not the case, something odd is happening, and the crash is appropriate.
        return func(*[a[0] for a in args], **{k: v[0] for k, v in kwargs.items()})

    funcs = plist(_ensure_len(len(self), func))
    if plist.all(funcs, isinstance, STRING_TYPES):
      funcs = plist.__getattribute__(self, funcs)
      return plist([funcs[i](*[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

    if psplit > 0:
      pool = _get_thread_pool(psplit, len(self))
      call_args = [pdict(x=x, i=i) for i, x in enumerate(self)]
      if paslist:
        if psplat:
          map_func = lambda ca: plist(funcs[ca.i](*ca.x.aslist() + [a[ca.i] for a in args], **{k: v[ca.i] for k, v in kwargs.items()}), root=ca.x.__root__)
        else:
          map_func = lambda ca: plist(funcs[ca.i](ca.x.aslist(), *[a[ca.i] for a in args], **{k: v[ca.i] for k, v in kwargs.items()}), root=ca.x.__root__)
      else:
        if psplat:
          map_func = lambda ca: funcs[ca.i](*list(ca.x) + [a[ca.i] for a in args], **{k: v[ca.i] for k, v in kwargs.items()})
        else:
          map_func = lambda ca: funcs[ca.i](ca.x, *[a[ca.i] for a in args], **{k: v[ca.i] for k, v in kwargs.items()})
      return plist(pool.map(map_func, call_args, chunksize=_get_thread_chunksize(psplit, len(self))), root=self.__root__)

    if paslist:
      if psplat:
        return plist([plist(funcs[i](*x.aslist() + [a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}), root=x.__root__) for i, x in enumerate(self)], root=self.__root__)
      return plist([plist(funcs[i](x.aslist(), *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}), root=x.__root__) for i, x in enumerate(self)], root=self.__root__)
    else:
      if psplat:
        return plist([funcs[i](*list(x) + [a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
      return plist([funcs[i](x, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

  def reduce(self, func, *args, **kwargs):
    """Apply a function repeatedly to its own result, returning a plist of length at most 1.

    `reduce` can be initialized either by using the `initial_value` keyword argument,
    or by the first value in `args`, if anything is passed to `args`, or from the first value
    in `self`, if the other options are not present.

    Examples:

    This is an example of passing `initial_value` as the first value in `args`:
    ```python
    s = 'foo bar was a baz of bin'
    pl = plist['foo', 'bar', 'baz', 'bin']
    reduced = pl.reduce(lambda s, x, y: qj(s).replace(x, y), s, pl._[::-1])
    # Logs:
    #   qj: <pstar> reduce: s <3451>: foo bar was a baz of bin
    #   qj: <pstar> reduce: s <3451>: oof bar was a baz of bin
    #   qj: <pstar> reduce: s <3451>: oof rab was a baz of bin
    #   qj: <pstar> reduce: s <3451>: oof rab was a zab of bin
    assert (reduced.aslist() ==
            ['oof rab was a zab of nib'])
    assert (reduced.root().aslist() ==
            ['foo bar was a baz of bin'])
    assert (reduced.root().root() is pl)
    ```

    The same thing, but using the `initial_value` keyword argument:
    ```python
    reduced = pl.reduce(lambda s, x, y: qj(s).replace(x, y), pl._[::-1], initial_value=s)
    assert (reduced.aslist() ==
            ['oof rab was a zab of nib'])
    assert (reduced.root().aslist() ==
            ['foo bar was a baz of bin'])
    assert (reduced.root().root() is pl)
    ```

    Using the first value in `self` for the initial value:
    ```python
    pl = plist[1, 2, 3, 4, 5]
    reduced = pl.reduce(lambda x, y, z: (x + y) * z, z=pl[::-1])
    assert (reduced.aslist() ==
            [466])
    ```
    Any additional `args` or `kwargs` values will be passed through to `func` at each call,
    in parallel to values of `self`. Note that `plist` arguments of the same length as `self`
    get passed through starting at the 0th element, and going until there are no more elements
    of `self`. If no value was passed for `initial_value`, this means that any additional
    arguments will only use `n-1` values. For example, in the code above, `z` ranges from 5 to
    2, producing the following computation:
    ```python
    assert ((((((1 + 2) * 5 + 3) * 4 + 4) * 3 + 5) * 2) ==
            466)
    ```

    When `self` is a grouped `plist`, `pepth` determines which groups are reduced over:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0), pdict(foo=3, bar=1), pdict(foo=4, bar=0)])
    (foo.bar == 0).baz = 3 + (foo.bar == 0).foo
    (foo.bar == 1).baz = 6
    foo.bin = (foo.baz + foo.bar) * foo.foo
    by_bar_baz_bin = foo.bar.groupby().baz.groupby().bin.groupby()
    assert (by_bar_baz_bin.aslist() ==
            [[[[{'bar': 0, 'baz': 3, 'bin': 0, 'foo': 0}]],
              [[{'bar': 0, 'baz': 5, 'bin': 10, 'foo': 2}]],
              [[{'bar': 0, 'baz': 7, 'bin': 28, 'foo': 4}]]],
             [[[{'bar': 1, 'baz': 6, 'bin': 7, 'foo': 1}],
               [{'bar': 1, 'baz': 6, 'bin': 21, 'foo': 3}]]]])

    import operator as op
    assert (by_bar_baz_bin.foo.reduce(op.add, initial_value=0).aslist() ==
            [10])
    assert (by_bar_baz_bin.foo.reduce_(op.add, initial_value=0).aslist() ==
            [[6], [4]])
    assert (by_bar_baz_bin.foo.reduce__(op.add, initial_value=0).aslist() ==
            [[[0], [2], [4]], [[4]]])
    assert (by_bar_baz_bin.foo.reduce___(op.add, initial_value=0).aslist() ==
            [[[[0]], [[2]], [[4]]], [[[1], [3]]]])
    ```
    Notice that the deepest reduction actually returns a reconstruction of the input plist,
    `by_bar_baz_bin.foo`, because at that level every element is in its own plist.

    You can also pass a list of functions to apply. The first function is applied to the
    broadest layer of the plist. Any additional layers consume a function. If the functions
    run out before the last layer, all the deeper layers get the last function from the list.
    If the layers run out before the functions do, deeper functions are not used in the
    reduction.
    ```python
    assert (by_bar_baz_bin.foo.reduce_(op.add, 0).reduce(op.mul, 1).aslist() ==
            [24])
    assert (by_bar_baz_bin.foo.reduce([op.mul, op.add], 0).aslist() ==
            [24])
    ```
    Note how `op.add` is applied to the deepest layers in both examples, and `op.mul` is only applied
    to the outermost plist, performing `6 * 4`.

    You can also set `initial_value` using a plist of the same structure:
    ```python
    assert (by_bar_baz_bin.foo.reduce(op.add, by_bar_baz_bin.baz).aslist() ==
            [37])
    assert (by_bar_baz_bin.foo.reduce([op.mul, op.add, op.mul, op.add], initial_value=by_bar_baz_bin.baz).aslist() ==
            [1323])
    ```

    Note that `reduce` does not currently provide a good mechanism for using a function of more than two arguments
    while reducing a deep plist, as that would require a reduction operation to be provided for each additional argument.
    Therefore, attempting to reduce a deep plist with a multiargument function is likely to crash or give unexpected
    results, and is not recommended.

    Args:
      func: function to call. Must take at least two positional arguments of the same type as `self`,
            and return a value of that type.
      *args: Additional arguments to pass to func at each step. If `initial_value` is not in
             `kwargs`, then the first value in `args` is used as `initial_value`.
      **kwargs: Additional kwargs to pass to `func`. If `initial_value` is passed, it is
                removed from `kwargs` and used as the first argument passed to `func` on
                the first call.
    """
    sentinal = object()
    initial_value = sentinal
    start = 0
    try:
      rargs = [_ensure_len(len(self), a, strict=True) for a in args]
      rkwargs = {
          k: _ensure_len(len(self), v, strict=True) for k, v in kwargs.items()
      }
      next_funcs = func
      if isinstance(next_funcs, list) and len(next_funcs):
        if len(next_funcs) == 1:
          func = next_funcs = next_funcs[0]
        else:
          func, next_funcs = next_funcs[0], next_funcs[1:]
      new_plist = plist([x.reduce(next_funcs, *[a[i] for a in rargs], **{k: v[i] for k, v in rkwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
      initial_value = new_plist[0]
      start = 1
      if kwargs.pop('initial_value', sentinal) == sentinal:
        if args:
          args = args[1:]
    except Exception as e:
      new_plist = self

    initial_value = kwargs.pop('initial_value', initial_value)
    if initial_value == sentinal:
      if args:
        initial_value, args = args[0], args[1:]
      elif len(new_plist):
        initial_value = new_plist[0]
        start = 1
      else:
        raise ValueError('plist.reduce must be called with either an initial value or on a non-empty plist.')

    args = [_ensure_len(len(new_plist), a, strict=True)[:-start or None] for a in args]
    kwargs = {
        k: _ensure_len(len(new_plist), v, strict=True)[:-start or None] for k, v in kwargs.items()
    }

    cur_val = initial_value
    for i, x in enumerate(new_plist[start:]):
      cur_val = func(cur_val, x, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()})

    return plist([cur_val], root=plist([initial_value], root=new_plist.__root__)).ungroup()

  def filter(self, func=bool, *args, **kwargs):
    """Filter `self` by an arbitrary function on elements of `self`, forwarding arguments.

    `filter` always returns the root of the filtered `plist`.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.filter().aslist() ==
            [dict(foo=1, bar=1), dict(foo=2, bar=0)])
    assert (foos.foo.filter(lambda x: x < 2).aslist() ==
            [dict(foo=0, bar=0), dict(foo=1, bar=1)])

    (foos.bar == 0).bin = 'zero'
    (foos.bar == 1).bin = 1
    assert (foos.bin.filter(isinstance, str).aslist() ==
            [{'bar': 0, 'bin': 'zero', 'foo': 0}, {'bar': 0, 'bin': 'zero', 'foo': 2}])
    ```

    Args:
      func: callable. Defaults to `bool`. Return value will be cast to `bool`.
      *args: Arguments to pass to `func`.
      **kwargs: Keyword arguments to pass to `func`, after extracting the same arguments as `plist.apply`.

    Returns:
      `plist` resulting from filtering out elements of `self` for whom `func` evaluated to a `False` value.
    """
    return self.apply(func, *args, **kwargs).apply(bool) == True

  def qj(self, *args, **kwargs):
    """Applies logging function qj to self for easy in-chain logging.

    `qj` is a debug logging function. Calling `plist.qj()` is often the fastest way
    to begin debugging an issue.

    See [qj](https://github.com/iansf/qj) for detailed information on using `qj`.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.foo.qj('foo').aslist() ==
            [0, 1, 2])
    # Logs:
    # qj: <calling_module> calling_func: foo <3869>: [0, 1, 2]
    ```

    Args:
      *args: Arguments to pass to `qj`.
      **kwargs: Keyword arguments to pass to `qj`.

    Returns:
      `self`
    """
    call_pepth = kwargs.pop('call_pepth', 0)
    return qj(self, _depth=4 + call_pepth, *args, **kwargs)

  ##############################################################################
  # Grouping and sorting methods.
  ##############################################################################
  def groupby(self):
    """Group `self.root()` by the values in `self` and return `self.root()`.

    Examples:

    Given a plist:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    foo_by_bar = foo.bar.groupby()
    assert (foo_by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    ```
    Note that foo_by_bar now has two nested plists. The first inner plist has
    the two pdicts where `foo.bar == 0`. The second inner plist has the
    remaining pdict where `foo.bar == 1`.

    Calling groupby again:
    ```python
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    ```
    Now foo_by_bar_foo has two nested layers of inner plists. The outer nest
    groups the values by `bar`, and the inner nest groups them by `foo`.

    groupby always operates with leaf children of the plist, and it always adds
    new groups as subgroups of the current innermost group.

    Grouping relies on the values being hashable. If, for some reason, you need
    to group by a non-hashable value, you should convert it to a hashable
    representation first, for example using `plist.pstr()` or `plist.apply(id)`:
    ```python
    foo = plist([{'bar': [1, 2, 3]}, {'bar': [1, 2, 3]}])
    try:
      foo_by_bar_crash = foo.bar.groupby()  # CRASHES!
    except Exception as e:
      assert (isinstance(e, TypeError))
    foo_by_bar_pstr = foo.bar.pstr().groupby()
    assert (foo_by_bar_pstr.aslist() ==
            [[{'bar': [1, 2, 3]},
              {'bar': [1, 2, 3]}]])
    foo_by_bar_id = foo.bar.apply(id).groupby()
    assert (foo_by_bar_id.aslist() ==
            [[{'bar': [1, 2, 3]}],
             [{'bar': [1, 2, 3]}]])
    ```
    Note that in the example above, using `pstr()` probably gives the intended
    result of grouping both elements together, whereas `apply(id)` gives the
    unsurprising result of putting each element into its own group.

    Returns:
      plist with one additional layer of internal plists, where each such plist
      groups together the root elements based on the values in this plist.
    """
    try:
      return plist([x.groupby() for x in self])
    except Exception:
      groups = collections.OrderedDict()
      for i, x in enumerate(self):
        if x not in groups:
          groups[x] = plist()
        groups[x].append(self.__root__[i])
      return plist(groups.values())

  def enum(self):
    """Wrap the current `plist` values in tuples where the first item is the index.

    Examples:
    ```python
    pl = plist['a', 'b', 'c']
    assert (pl.enum().aslist() ==
            [(0, 'a'), (1, 'b'), (2, 'c')])

    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    assert (by_bar.foo.enum_().aslist() ==
            [[(0, 0), (1, 2)], [(0, 1)]])
    ```

    Returns:
      `plist` of `(i, x)` pairs from calling `enumerate` on `self`.
    """
    return plist(enumerate(self), root=self.__root__)

  def join(self):
    """Adds and returns an outer `plist` around `self`.

    Examples:

    `join` is useful when you wish to call a function on the top-level plist,
    but you don't want to stop your call chain:
    ```python
    foo = plist([{'bar': [1, 2, 3]}, {'bar': [4, 5, 6]}])
    assert (foo.aslist() ==
            [{'bar': [1, 2, 3]},
             {'bar': [4, 5, 6]}])
    arr1 = np.array(foo.bar.pstr().groupby().bar)
    assert (np.all(arr1 ==
                   np.array([[[1, 2, 3]],
                             [[4, 5, 6]]])))
    arr2 = foo.bar.pstr().groupby().bar.np()
    assert (np.all(np.array(arr2.aslist()) ==
                   np.array([np.array([[1, 2, 3]]),
                             np.array([[4, 5, 6]])])))
    arr3 = foo.bar.pstr().groupby().bar.join().np()
    assert (np.all(np.array(arr3.aslist()) ==
                   np.array([np.array([[[1, 2, 3]],
                                      [[4, 5, 6]]])])))
    assert (np.any(arr1 != arr2[0]))
    assert (np.all(arr1 == arr3[0]))
    ```
    In the example above, calling `np.array` on the grouped plist gives a
    particular array structure, but it does not return a plist, so you can't as
    naturally use that array in ongoing computations while keeping track of
    the correspondence of the array with the original data in `foo`.

    Calling plist.np() directly on the grouped plist gives a different result,
    however, as shown in `arr2`. The array is missing one dimension relative to
    the call that generated `arr1`.

    Instead, it is easy to call `plist.join()` before calling `plist.np()` in
    this case in order to get the same result of passing `self` to `np.array()`,
    but the advantage is that the numpy array is still wrapped in a plist, so it
    can be used in follow-on computations.

    Returns:
      plist with one additional level of nesting.
    """
    return plist([self])

  def sortby(self, key=None, reverse=False):
    """Sorts `self` and `self.root()` in-place and returns `self`.

    `sortby` and `groupby` work together nicely to create sorted, nested plists.
    Note that `sortby` modifies and returns `self`, whereas `groupby` returns a
    new `plist` with a new root. This is because `sortby` doesn't change the
    structure of the plist, only the order of its (or its children's) elements.

    Examples:

    A basic sort:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    bar_sorted = foos.bar.sortby()
    assert (bar_sorted.aslist() ==
            [0, 0, 1])
    foos_sorted_by_bar = bar_sorted.root()
    assert (foos_sorted_by_bar.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    ```

    Sorting with groups works in the same way -- the sort is applied to each
    group of `self`:
    ```python
    by_bar = foos.bar.groupby()
    assert (by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    by_bar_sorted = by_bar.bar.sortby(reverse=True)
    assert (by_bar_sorted.aslist() ==
            [[1], [0, 0]])
    by_bar_sorted = by_bar_sorted.root()
    assert (by_bar_sorted.aslist() ==
            [[{'foo': 1, 'bar': 1}],
             [{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}]])
    ```

    Args:
      key: Key function to pass to `sorted`. Defaults to the identity function.
           See the python documentation for `sorted` for more information.
      reverse: Boolean specifying whether to sort in reverse order or not.

    Returns:
      `self`, sorted.
    """
    key = key or (lambda x: x)
    sorted_inds = [i for i, _ in sorted(enumerate(self), key=lambda x: key(x[1]), reverse=reverse)]
    self.__root__[:] = self.__root__[sorted_inds]
    if self is not self.__root__:
      self[:] = self[sorted_inds]
    return self

  def ungroup(self, r=1, s=None):
    """Inverts the last grouping operation applied and returns a new plist.

    `ungroup` undoes the last `groupby` operation by default. It removes
    groupings in the inverse order that they are applied in -- `groupby`
    always adds new groups at the inner most layer, so `ungroup` removes
    groups from the innermost layer. It does not undo any implicit sorting
    caused by the `groupby` operation, however.

    Examples:
    ```python
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.sortby().groupby()
    assert (by_bar.ungroup().aslist() ==
            foos.aslist())

    by_bar[0].baz = 6
    by_bar[1].baz = by_bar[1].foo * 2
    by_bar_baz = by_bar.baz.groupby()
    assert (by_bar_baz.ungroup().aslist() ==
            by_bar.aslist())
    assert (by_bar_baz.ungroup(2).aslist() ==
            foos.aslist())
    assert (by_bar_baz.ungroup(-1).aslist() ==
            by_bar.ungroup(-1).aslist())
    ```

    Args:
      r: Integer value for the number of groups to remove. If `r == 0`, no
         groups are removed. If it is positive, that many groups must be
         removed, or `upgroup` raises a `ValueError`. If `r < 0`, all groups in
         this plist are removed, returning a flat plist.
      s: Successor object. Do not pass -- used to track how many ungroupings
         have happened so that `ungroup` knows when to stop.

    Returns:
      New plist with one or more fewer inner groups, if there were any.

    Raises:
      ValueError: If there are fewer groups to ungroup than requested.
    """
    s = _successor(r) if s is None else s
    if s.v == 0:
      return self
    new_items = []
    try:
      cs = s
      new_xs = []
      for x in self:
        cs = _successor(s.v)
        new_xs.append(x.ungroup(cs.v, cs))
      # Assumes that all children have the same depth.
      # The plist is malformed if that isn't the case, and things will crash at some point.
      s.v = cs.v
      if s.v == 0:
        return plist(new_xs)
      for x in new_xs:
        new_items.extend(x)
    except Exception:
      if s.v == 0:
        raise ValueError('Called ungroup on a plist that has non-group children')
      return self
    s.p()
    return plist(new_items)

  def zip(self, *others):
    """Zips `self` with `others`, recursively.

    Examples:
    ```python
    pl1 = plist['a', 'b', 'c']
    pl2 = plist[1, 2, 3]
    pl3 = plist['nother', 'ig', 'odebase']
    assert (pl2.zip(pl1, pl3).aslist() ==
            [(1, 'a', 'nother'), (2, 'b', 'ig'), (3, 'c', 'odebase')])

    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    assert (by_bar.bar.zip(by_bar.foo).aslist() ==
            [[(0, 0), (0, 2)], [(1, 1)]])
    ```

    Args:
      *others: `iterable`s that have the same length as `self`.

    Returns:
      New `plist` with the same structure as `self`.

    Raises:
      `ValueError` if `self` and each `iterable` in `others` don't all have the same length at
      level `zip` is initially called at.
    """
    plothers = plist(others)
    if plothers.any(lambda x: len(x) != len(self)):
      raise ValueError('plist.zip arguments must all have the same length as self (%d)' % len(self))
    try:
      return plist([x.zip(*plothers.__getitem___(i)) for i, x in enumerate(self)], root=self.__root__)
    except Exception:
      pass
    zipped = [x for x in zip(self, *others)]  # 3.6 compatibility
    return plist(zipped, root=self.__root__[0:len(zipped):1])

  ##############################################################################
  # Additional filtering methods.
  ##############################################################################
  def nonempty(self, r=0):
    """Returns a new `plist` with empty sublists removed.

    Examples:

    `nonempty` is useful in combination with grouping and filtering:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    foo_by_bar = foo.bar.groupby()
    assert (foo_by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    filtered = foo_by_bar.foo != 1
    assert (filtered.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             []])
    filtered_nonempty = filtered.nonempty()
    assert (filtered_nonempty.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}]])
    ```

    If the plist is deep, multiple levels of empty sublists can be removed at
    the same time:
    ```python
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    filtered = foo_by_bar_foo.foo != 1
    assert (filtered.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    filtered_nonempty_0 = filtered.nonempty()
    assert (filtered_nonempty_0.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    filtered_nonempty_1 = filtered.nonempty(1)
    assert (filtered_nonempty_1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]]])
    filtered_nonempty_n1 = filtered.nonempty(-1)
    assert (filtered_nonempty_n1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]]])
    ```
    Note that `filtered_nonempty_0` is identical to `filteed`, since there are
    no empty sublists at the top level. In this example, `filtered_nonempty_1`
    and `filtered_nonempty_n1` give the same result -- the deepest empty sublist
    is removed, and then the next deepest empty sublist is removed.

    It is also possible to remove empty sublists only at deeper levels, using
    the two ways to call functions on sublists -- passing `pepth` and adding `_`
    to the method name:
    ```python
    filtered_nonempty_p1 = filtered.nonempty(pepth=1)
    assert (filtered_nonempty_p1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             []])
    filtered_nonempty_u1 = filtered.nonempty_()
    assert (filtered_nonempty_u1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             []])
    ```
    `filtered_nonempty_p1` and `filtered_nonempty_u1` both remove a single layer
    of empty sublists starting from one layer into `filtered`.

    Args:
      r: Integer value for the number of times to recurse. Defaults to 0, which
         causes only empty direct children of `self` to be removed. If `r > 0`,
         `nonempty` recurses `r` times, and then removes empty sublists at that
         depth and empty sublists back up the recursive call chain. If `r < 0`,
         `nonempty` recurses as deep as it can, and then removes empty sublists
         back up the recursive call chain.

    Returns:
      New plist with empty sublist removed.
    """
    if r != 0:
      try:
        new_plist = plist([x.nonempty(r=r - 1) for x in self if len(x)])
      except Exception:
        new_plist = self
    else:
      new_plist = self
    return plist([x for x in new_plist if len(x)],
                 root=plist([self.__root__[i] for i, x in enumerate(new_plist) if len(x)]))

  def puniq(self):
    """Returns a new `plist` with only a single element of each value in `self`.

    Examples:

    `puniq` reduces the values of the groups of self using an equality check:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    reduced = foo.bar.puniq()
    assert (reduced.aslist() ==
            [0, 1])
    assert (reduced.root().aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    ```

    Grouped plists
    ```python
    foo_by_bar = foo.bar.groupby()
    assert (foo_by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    reduced = foo_by_bar.bar.puniq()
    assert (reduced.aslist() ==
            [[0], [1]])
    assert (reduced.root().aslist() ==
            [[{'foo': 0, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    ```

    The equality check respects the subgroups of self:
    ```python
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    reduced_no_effect = foo_by_bar_foo.bar.puniq()
    assert (reduced_no_effect.aslist() ==
            [[[0], [0]], [[1]]])
    assert (reduced_no_effect.root().aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    ```

    As with `plist.groupby`, `preduce_eq` relies on the values being hashable.
    If, for some reason, you need to reduce by a non-hashable value, you should
    convert it to a hashable representation first, for example using
    `plist.pstr()` or `plist.apply(id)`:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=0, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 0, 'bar': 0}])
    try:
      reduced_crash = foo.puniq()  # CRASHES!
    except Exception as e:
      assert (isinstance(e, TypeError))
    reduced_pstr = foo.pstr().puniq()
    assert (reduced_pstr.aslist() ==
            ["{'bar': 0, 'foo': 0}",
             "{'bar': 1, 'foo': 1}"])
    assert (reduced_pstr.root().aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    reduced_id = foo.apply(id).puniq()
    assert (reduced_id.root().aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 0, 'bar': 0}])
    ```
    In the last case, since each of the elements of `foo` are unique pdicts,
    reducing by `plist.apply(id)` has no useful effect, but if there had been
    any duplicates in the elements of `foo`, they would have been removed.

    Returns:
      New `plist` with a new `root` where there is only one example of each value
      in each sublist. The corresponding root element is the first element in
      `self.root()` that has that value.
    """
    try:
      if self.enum().all(lambda x: x[1].__root__.pequal(self.__root__[x[0]])):
        new_plist = plist([x.puniq() for x in self])
        new_plist.__root__ = plist([x.__root__ for x in new_plist])
        return new_plist
      return plist([x.puniq() for x in self], root=self.__root__)
    except Exception:
      pass
    vals = set()
    new_items = []
    new_roots = []
    not_root = (self is not self.__root__)
    for i, x in enumerate(self):
      if x in vals:
        continue
      vals.add(x)
      new_items.append(x)
      if not_root:
        new_roots.append(self.__root__[i])
    if not_root:
      return plist(new_items, root=plist(new_roots))
    return plist(new_items)

  preduce_eq = puniq

  def remix(self, *args, **kwargs):
    r"""Returns a new `plist` of `pdicts` based on selected data from `self`.

    Examples:

    `remix` allows you to easily restructure your data into a manageable form:
    ```python
    foo = plist([{'foo': 0, 'bar': {'baz': 13, 'bam': 0, 'bin': 'not'}},
                 {'foo': 1, 'bar': {'baz': 42, 'bam': 1, 'bin': 'good'}},
                 {'foo': 2, 'bar': {'baz': -9, 'bam': 0, 'bin': 'data'}}])
    rmx = foo.remix('foo', baz=foo.bar.baz)
    assert (rmx.aslist() ==
            [{'foo': 0, 'baz': 13},
             {'foo': 1, 'baz': 42},
             {'foo': 2, 'baz': -9}])
    ```
    Note that `rmx.baz` gets its values from `foo.bar.baz` in a natural manner.

    If `remix` is called on a grouped plist, the result is still a flat plist
    of flat pdicts, but the values in the pdicts are themselves pdicts:
    ```python
    foo_by_bam = foo.bar.bam.groupby()
    assert (foo_by_bam.aslist() ==
            [[{'foo': 0, 'bar': {'bam': 0, 'baz': 13, 'bin': 'not'}},
              {'foo': 2, 'bar': {'bam': 0, 'baz': -9, 'bin': 'data'}}],
             [{'foo': 1, 'bar': {'bam': 1, 'baz': 42, 'bin': 'good'}}]])
    rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz)
    assert (rmx_by_bam.aslist() ==
            [{'foo': [0, 2], 'baz': [13, -9]},
             {'foo': [1],    'baz': [42]}])
    ```

    This behavior can be useful when integrating with pandas, for example:
    ```python
    df = rmx_by_bam.pd()
    assert (str(df) ==
            '        baz     foo\n'
            '0  [13, -9]  [0, 2]\n'
            '1      [42]     [1]')
    ```

    If you instead want `remix` to return grouped pdicts, just pass `pepth=-1`
    to have it execute on the deepest plists, as with any other call to a plist:
    ```python
    rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz, pepth=-1)
    assert (rmx_by_bam.aslist() ==
            [[{'foo': 0, 'baz': 13},
              {'foo': 2, 'baz': -9}],
             [{'foo': 1, 'baz': 42}]])
    ```

    Args:
      *args: List of property names of items in `self` to include in the remix.
      **kwargs: Key/value pairs where the key will be a new property on items in
                the remix and the value is a deepcast and set to that key.

    Returns:
      Flat `plist` of flat `pdicts` based on data from `self` and the passed
      arguments and keyword arguments.
    """
    kwargs = {
        k: _ensure_len(len(self), v, strict=True) for k, v in kwargs.items()
    }
    new_items = []
    for i, x in enumerate(self):
      y = pdict(
          **{
              a: (hasattr(x, a) and getattr(x, a)) or x[a]
              for a in args
          }
      )
      y.update({k: v[i] for k, v in kwargs.items()})
      new_items.append(y)
    return plist(new_items)

  ##############################################################################
  # Structure-relevant methods
  ##############################################################################

  # Depth, length, shape, and structure.
  def pdepth(self, s=False):
    """Returns a `plist` of the recursive depth of each leaf element, from 0.

    Examples:

    `pdepth` returns a plist of the same plist structure as self:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.pdepth().aslist() ==
            [0])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.pdepth().aslist() ==
            [[[2], [2]], [[2]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.pdepth().aslist() ==
            [[[2], [2]], [[]]])
    ```

    Since the depth values are always equal or empty in well-formed plists, it
    is sometimes more convenient to get the depth as a scalar value. Pass a True
    value to the first parameter (`s` for 'scalar'):
    ```python
    assert (foo.pdepth(s=1) == 0)
    assert (foo_by_bar_foo.pdepth(1) == 2)
    assert (filtered.pdepth(True) == 2)
    ```

    Args:
      s: Boolean that controls whether a scalar is returned (when `True`) or a
         plist of the same structure as self (when `False`, the default).

    Returns:
      plist whose elements are the recursive depth of the leaf children, or a
      scalar representing the maximum depth encountered in self if `s` is
      `True`.
    """
    try:
      d = plist([x.pdepth() + 1 for x in self], root=self.__root__)
    except Exception:
      d = plist([0], root=self.__root__)
    if s:
      d = d.ungroup(-1).preduce_eq()
      if d:
        return max(d)
      return 0
    return d

  def plen(self, r=0, s=False):
    """Returns a `plist` of the length of a recursively-selected layer of `self`.

    Examples:

    `plen` returns a plist of the same depth as self, up to `r`:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.plen().aslist() ==
            [3])
    assert (foo.plen(1).aslist() ==
            [3])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.plen().aslist() ==
            [2])
    assert (foo_by_bar_foo.plen(r=1).aslist() ==
            [[3]])
    assert (foo_by_bar_foo.plen(2).aslist() ==
            [[[3]]])
    assert (foo_by_bar_foo.plen(-1).aslist() ==
            [[[3]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.plen().aslist() ==
            [2])
    assert (filtered.plen(-1).aslist() ==
            [[[2]]])
    ```

    Since the depth values are always equal or empty in well-formed plists, it
    is sometimes more convenient to get the depth as a scalar value. Pass a True
    value to the first parameter (`s` for 'scalar'):
    ```python
    assert (foo.plen(s=1) == 3)
    assert (foo_by_bar_foo.plen(r=2, s=1) == 3)
    assert (filtered.plen(-1, s=True) == 2)
    ```

    Args:
      r: Target recursion depth. Defaults to 0. Set to -1 to recurse as deep as
         possible.
      s: Boolean that controls whether a scalar is returned (when `True`) or a
         `plist` of the same depth as `self` (when `False`, the default).

    Returns:
      `plist` whose depth equals the requested recursion depth (or less, if
      `r > self.pdepth()`), containing a single value which is the number of
      `plist` elements at that depth, or that value as a scalar if `s` is `True`.
    """
    l = None
    if r != 0:
      try:
        l = plist([sum(x.plen(r - 1) for x in self)], root=self.__root__)
      except Exception:
        pass
    if l is None:
      l = plist([len(self)], root=self.__root__)
    if s:
      l = l.ungroup(-1).preduce_eq()
      if l:
        return max(l)
      return 0
    return l

  def pshape(self):
    """Returns a `plist` of the same structure as `self`, filled with leaf lengths.

    Examples:

    `pshape` returns a plist of the same structure as `self`:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.pshape().aslist() ==
            [3])

    foo_by_bar = foo.bar.groupby()
    assert (foo_by_bar.aslist() ==
            [[{'bar': 0, 'foo': 0},
              {'bar': 0, 'foo': 2}],
             [{'bar': 1, 'foo': 1}]])
    assert (foo_by_bar.pshape().aslist() ==
            [[2], [1]])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.pshape().aslist() ==
            [[[1], [1]], [[1]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.pshape().aslist() ==
            [[[1], [1]], [[]]])
    ```

    Returns:
      New `plist` of the same structure as `self`, where each leaf `plist` has a
      single element, which is the length of the corresponding leaf `plist` in
      `self`.
    """
    try:
      return plist([x.pshape() for x in self], root=self.__root__)
    except Exception:
      return plist([len(self)], root=self.__root__)

  def pstructure(self):
    """Returns a `list` of the number of elements in each layer of `self`.

    Gives a snapshot view of the structure of `self`. The length of the returned
    list is the depth of `self`. Each value in the list is the result of calling
    `self.plen(r)`, where `r` ranges from 0 to `self.pdepth()`. `plen(r)` gives
    the sum of the lengths of all plists at layer `r`.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.pstructure().aslist() ==
            [3])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.pstructure().aslist() ==
            [2, 3, 3])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.pstructure().aslist() ==
            [2, 3, 2])
    ```

    Returns:
      A `list` (not a `plist`) of `self.pdepth()` integers, where each integer is
      the number of elements in all `plist`s at that layer, 0-indexed according to
      depth.
    """
    s = []
    for r in range(self.pdepth(True) + 1):
      s.extend(self.plen(r).ungroup(-1))
    return plist(s, root=self.__root__)

  # Fill with different values.
  def lfill(self, v=0, s=None):
    """Returns a **`list`** with the structure of `self` filled in order from `v`.

    Identical to `plist.pfill()`, but returns a **`list`** instead of a `plist`.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.lfill() ==
            [0, 1, 2])
    assert (foo.lfill(-7) ==
            [-7, -6, -5])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.lfill() ==
            [[[0], [1]], [[2]]])
    assert (foo_by_bar_foo.lfill_() ==
            [[[0], [1]], [[0]]])
    assert (foo_by_bar_foo.lfill(pepth=2) ==
            [[[0], [0]], [[0]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.lfill(3) ==
            [[[3], [4]], [[]]])
    ```

    Args:
      v: Integer. The value to start filling from. Defaults to 0.
      s: Successor object. Do not pass -- used to track the count of calls
         across the recursive traversal of `self`.

    Returns:
      A **`list`** (not a `plist`) of possibly nested `list`s where each leaf element is
      an integer, starting with the value of `v` in the 'top left' element of
      the structure.
    """
    s = _successor(v - 1) if s is None else s
    try:
      return [x.lfill(s=s) for x in self]
    except Exception:
      return [s.s() for _ in range(len(self))]

  def pfill(self, v=0, s=None):
    """Returns a `plist` with the structure of `self` filled in order from `v`.

    Identical to `plist.lfill()`, but returns a **`plist`** instead of a `list`.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.pfill().aslist() ==
            [0, 1, 2])
    assert (foo.pfill(-7).aslist() ==
            [-7, -6, -5])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.pfill().aslist() ==
            [[[0], [1]], [[2]]])
    assert (foo_by_bar_foo.pfill_().aslist() ==
            [[[0], [1]], [[0]]])
    assert (foo_by_bar_foo.pfill(pepth=2).aslist() ==
            [[[0], [0]], [[0]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.pfill(3).aslist() ==
            [[[3], [4]], [[]]])
    ```

    Args:
      v: Integer. The value to start filling from. Defaults to 0.
      s: Successor object. Do not pass -- used to track the count of calls
         across the recursive traversal of `self`.

    Returns:
      A `plist` of possibly nested `plist`s where each leaf element is an integer,
      starting with the value of `v` in the 'top left' element of the structure.
    """
    s = _successor(v - 1) if s is None else s
    try:
      return plist([x.pfill(s=s) for x in self], root=self.__root__)
    except Exception:
      return plist([s.s() for _ in range(len(self))], root=self.__root__)

  def pleft(self):
    """Returns a `plist` with the structure of `self` filled `plen(-1)` to 0.

    Convenience method identical to `-self.pfill(1) + self.plen(-1, s=True)`.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.pleft().aslist() ==
            [2, 1, 0])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.pleft().aslist() ==
            [[[2], [1]], [[0]]])
    assert (foo_by_bar_foo.pleft_().aslist() ==
            [[[1], [0]], [[0]]])
    assert (foo_by_bar_foo.pleft(pepth=2).aslist() ==
            [[[0], [0]], [[0]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    assert (filtered.pleft().aslist() ==
            [[[1], [0]], [[]]])
    ```

    This is useful for calling functions that have some global state that should
    change each time a new grouping is started, such as generating many plots
    from a single grouped plist using `pyplot`, where the function would need to
    call `plt.show()` after each group was completed:
    ```python
    def plot(x, remaining):
      plt.plot(x)

      if remaining == 0:
        plt.show()

    (foo.bar == 0).baz = 3 + (foo.bar == 0).foo
    (foo.bar == 1).baz = 6
    foo.bin = (foo.baz + foo.bar) * foo.foo
    by_bar_baz_bin = foo.bar.groupby().baz.groupby().bin.groupby()
    by_bar_baz_bin.foo.apply(plot, by_bar_baz_bin.pleft(pepth=2), pepth=2)
    ```

    Returns:
      A `plist` of possibly nested `plist`s where each leaf element is an integer,
      starting with `self.plen(-1)` in the 'top left' element of the structure
      and counting down to 0.
    """
    return -self.pfill(1) + self.plen(-1, s=True)

  def values_like(self, value=0):
    """Returns a `plist` with the structure of `self` filled with `value`.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    assert (foo.values_like(1).aslist() ==
            [1, 1, 1])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    assert (foo_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    assert (foo_by_bar_foo.values_like('foo').aslist() ==
            [[['foo'], ['foo']], [['foo']]])
    all_the_same_dict = foo_by_bar_foo.values_like({}, pepth=2)
    assert (all_the_same_dict.aslist() ==
            [[[{}], [{}]], [[{}]]])

    all_the_same_dict.ungroup(-1)[0].update(foo=1)
    assert (all_the_same_dict.aslist() ==
            [[[{'foo': 1}], [{'foo': 1}]], [[{'foo': 1}]]])

    filtered = foo_by_bar_foo.bar == 0
    assert (filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    tuples = filtered.values_like((1, 2, 3))
    assert (tuples.aslist() ==
            [[[(1, 2, 3)], [(1, 2, 3)]], [[]]])
    ```

    Note in the example above that filling with a mutable object like a `dict` gives
    a `plist` filled that single object, which might be surprising, but is the
    same as other common python idioms, such as:
    ```python
    all_the_same_dict = [{}] * 3
    assert (all_the_same_dict ==
            [{}, {}, {}])
    all_the_same_dict[0].update(foo=1)
    assert (all_the_same_dict ==
            [{'foo': 1}, {'foo': 1}, {'foo': 1}])
    ```

    Args:
      value: Value to fill the returned `plist` with. Can by any python object.

    Returns:
      A `plist` with the structure of `self` filled with `value`.
    """
    values = _ensure_len(len(self), value, strict=True)
    try:
      return plist([x.values_like(v) for x, v in zip(self, values)], root=self.__root__)
    except Exception:
      pass
    return plist([v for v in values], root=self.__root__)

  ##############################################################################
  # Calling-frame-modifying utility methods.
  ##############################################################################
  def me(self, name_or_plist='me', call_pepth=0):
    """Sets the current plist as a variable available in the caller's context.

    `me` is a convenience method to naturally enable long chaining to prepare
    the data in the `plist` for a future call to `apply` or some other call. It
    attempts to add the current `plist` to the caller's context, either as a
    local variable, or as a global (module-level) variable. Because it modifies
    the caller's frame, it is not recommended for production code, but can be
    useful in jupyter notebooks and colabs during exploration of datasets.

    Examples:

    Using `me` with a local variable requires that the variable already exist in
    the local context, and that it be a `plist`:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foo.baz = 3 * foo.foo + foo.bar
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0, 'baz': 0},
             {'foo': 1, 'bar': 1, 'baz': 4},
             {'foo': 2, 'bar': 0, 'baz': 6}])
    def new_context():
      me = plist()
      foo.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.bar)
    new_context()
    ```

    The same can work with a name of your choice:
    ```python
    def new_context():
      baz = plist()
      foo.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
    new_context()
    ```

    You can pass the `plist` you want to use instead:
    ```python
    def new_context():
      me2 = plist()
      foo.bar.groupby().baz.sortby_().groupby().me(me2).foo.plt().plot(me2.foo + 1)
    new_context()
    ```

    If there isn't a local variable of that name, `me()` will put the `plist` into
    the caller's `globals()` `dict` under the requested name. The following both
    work if there are no local or global variables named `me` or `baz`:
    ```python
    def new_context():
      foo.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.baz)
      foo.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
      del globals()['me']
      del globals()['baz']
    new_context()
    ```

    Args:
      name_or_plist: String naming a variable in the caller's context or the
                     global (module-level) context, or an existing plist. In
                     both cases, the variable will be overwritten with a plist
                     that is a shallow copy of `self`. Defaults to `'me'`.
      call_pepth: Do not pass. Used by `plist.__call__` to keep track of how
                  many stack frames occur between the caller and `me()`.

    Returns:
      `self`, permitting continued chaining.

    Raises:
      ValueError: If `name_or_plist` is a string, and that name appears in the
                  caller's local variables, but does not evaluate to a `plist`.
      ValueError: If something other than a string or a `plist` is passed to
                  `name_or_plist`.
    """
    try:
      call_pepth += 3
      f = inspect.currentframe()
      for _ in range(call_pepth):
        f = f.f_back

      if isinstance(name_or_plist, str):
        frame_locals = f.f_locals
        if name_or_plist in frame_locals:
          me = frame_locals[name_or_plist]
          if not isinstance(me, plist):
            raise ValueError('To use plist.me(name_or_plist) with a local variable named %s, it must be a plist object. Got %r.' % (name_or_plist, me))
        else:
          me = plist()
          f.f_globals[name_or_plist] = me
      elif isinstance(name_or_plist, plist):
        me = name_or_plist
      else:
        raise ValueError('plist.me(name_or_plist) requires that name_or_plist be either a str or a plist. Got %r.' % name_or_plist)

      if hasattr(list, 'clear'):
        list.clear(me)
      else:
        del me[:]
      list.extend(me, self)
      me.__root__ = self.__root__
    finally:
      # Delete the stack frame to ensure there are no memory leaks, as suggested
      # by https://docs.python.org/2/library/inspect.html#the-interpreter-stack
      del f
    return self

  def pand(self, name='__plist_and_var__', call_pepth=0):
    """Stores `self` into a `plist` of `tuple`s that gets extended with each call.

    `pand` is meant to facilitate building up tuples of values to be sent as
    a single block to a chained call to `apply`, or as `*args` when calling
    `plist.apply(psplat=True)`. The name is `pand` to evoke conjunction: the
    caller wants a `plist` with this *and* this *and* this.

    `pand` stores a variable in the caller's frame that isn't visible to the
    caller, but is visible to future calls to `pand` due to how `locals()`
    works.

    Examples:
    ```python
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foo.baz = 3 * foo.foo + foo.bar
    assert (foo.aslist() ==
            [{'foo': 0, 'bar': 0, 'baz': 0},
             {'foo': 1, 'bar': 1, 'baz': 4},
             {'foo': 2, 'bar': 0, 'baz': 6}])
    def new_context():
      assert (foo.bar.groupby().baz.groupby().foo.pand().root().bar.pand().ungroup()
                 .apply_(qj, '(foo, bar)') ==
              [[[(0, 0)],
                [(2, 0)]],
               [[(1, 1)]]])
    new_context()
    # Logs:
    #   qj: <pstar> apply: (foo, bar) <1249>: (0, 0)
    #   qj: <pstar> apply: (foo, bar) <1249>: (2, 0)
    #   qj: <pstar> apply: (foo, bar) <1249>: (1, 1)
    ```

    The same construction can be used with methods that expect the arguments
    individually, requiring the tuple to be expanded:
    ```python
    def new_context():
      (foo.bar.groupby().baz.groupby().foo.pand().root().bar.pstr().pand()
          .ungroup().apply_(qj, psplat=True, b=0))
    new_context()
    # Logs:
    #   qj: <pstar> apply: (foo, bar) <2876>: (0, 0)
    #   qj: <pstar> apply: (foo, bar) <2876>: (2, 0)
    #   qj: <pstar> apply: (foo, bar) <2876>: (1, 1)
    #   qj: <pstar> apply: (0, 0) <2876>: (0, 0)
    #   qj: <pstar> apply: (2, 0) <2876>: (2, 0)
    #   qj: <pstar> apply: (1, 1) <2876>: (1, 1)
    ```

    Building multiple tuples in the same context requires passing `name` to keep
    them separate:
    ```python
    def new_context():
      me = plist()
      assert (foo.bar.groupby().baz.groupby().me().foo.pand().root().bar.pand().ungroup()
                 .apply_(qj,
                         me.foo.pand('strs').root().bar.pand('strs').ungroup().pstr()) ==
              [[(0, 0),
                (2, 0)],
               [(1, 1)]])
    new_context()
    # Logs:
    #   qj: <pstar> apply: (0, 0) <1249>: (0, 0)
    #   qj: <pstar> apply: (2, 0) <1249>: (2, 0)
    #   qj: <pstar> apply: (1, 1) <1249>: (1, 1)
    ```
    Note that the construction above is hard to understand, and probably
    shouldn't be used.

    Args:
      name: String naming an available variable in the caller's context. Should
            only be passed if the calling frame needs to create multiple
            different `tuple`s. Defaults to '__plist_and_var__'. If a variable of
            the same name exists in the caller's context, `pand` will fail to
            write to it.
      call_pepth: Do not pass. Used by `plist.__call__` to keep track of how
                  many stack frames occur between the caller and `pand()`.

    Returns:
      The current `plist` of `tuple`s, with `self` added.

    Raises:
      ValueError: If the variable named by `name` is already present in the
                  caller's frame and is not a `plist`, or has different `pshape()`
                  than `self`.
    """
    try:
      call_pepth += 3
      f = inspect.currentframe()
      for _ in range(call_pepth):
        f = f.f_back

      frame_locals = f.f_locals
      if name in frame_locals:
        and_var = frame_locals[name]
        if not isinstance(and_var, plist):
          raise ValueError('plist.pand() expected a plist object with the name %s in the calling frame. Got %r.' % (name, and_var))
        if not self.pshape().pequal(and_var.pshape()):
          raise ValueError('plist.pand() found a previous plist object with an incompatible shape.\n'
                           '\tMake sure that all calls to plist.pand() in the same stack frame operate on plists with the same shape,'
                           ' or are called with different `name` arguments.\n'
                           '\tExpected %r, got %r.' % (self.pshape(), and_var.pshape()))
      else:
        and_var = self.values_like(tuple())
      and_var = and_var.apply(list, pepth=-1).apply(lambda x, y: x.append(y) or x, self, pepth=-1).apply(tuple, pepth=-1)

      frame_locals[name] = and_var

      return and_var
    finally:
      # Delete the stack frame to ensure there are no memory leaks, as suggested
      # by https://docs.python.org/2/library/inspect.html#the-interpreter-stack
      del f


# pylint: enable=line-too-long,invalid-name,g-explicit-length-test
# pylint: enable=broad-except,g-long-lambda
