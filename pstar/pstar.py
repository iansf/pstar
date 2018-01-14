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
"""pstar: replacements for common container classes.

Import with:
  from pstar import *
"""

import collections
from collections import defaultdict
import inspect
import operator
import sys
import types

import numpy as np
import pandas as pd
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
  """dict subclass where everything is automatically a property.

  Use with dot notation or subscript notation:
  ```
    p = pdict()
    p.foo = 1
    assert p['foo'] == p.foo == 1
  ```

  List subscripts also work and return a plist of the corresponding keys:
  ```
    p = pdict(foo=1, bar=2)
    assert p[['foo', 'bar']].aslist() == [1, 2]
  ```

  Setting with a list subscript also works, using a single element or a matching
  list for the values:
  ```
    p = pdict()
    p[['foo', 'bar']] = 1
    assert p[['foo', 'bar']].aslist() == [1, 1]
    p[['foo', 'bar']] = [1, 2]
    assert p[['foo', 'bar']].aslist() == [1, 2]
  ```

  pdict.update() returns self, rather than None, to support chaining:
  ```
    p = pdict(foo=1, bar=2)
    p.update(bar=3).baz = 4
    assert p.bar == 3
    assert 'baz' in p.keys()
  ```
  """

  def __init__(self, *a, **kw):
    dict.__init__(self, *a, **kw)
    self.__dict__ = self

  def __getitem__(self, key):
    if isinstance(key, list):
      return plist([self[k] for k in key], root=plist([KeyValue(k, self[k]) for k in key]))
    else:
      return dict.__getitem__(self, key)

  def __setitem__(self, key, value):
    if isinstance(key, list):
      value = _ensure_len(len(key), value)
      for k, v in zip(key, value):
        dict.__setitem__(self, k, v)
    else:
      dict.__setitem__(self, key, value)
    return self

  def __str__(self):
    delim = ', ' if len(self) < 8 else ',\n '
    s = delim.join('%s: %s' % (repr(k), repr(self[k])) for k in self.peys())
    return '{' + s + '}'

  __repr__ = __str__

  def update(self, *a, **kw):
    dict.update(self, *a, **kw)
    return self

  def copy(self):
    return pdict(dict.copy(self))

  def peys(self):
    return plist(sorted(self.keys()))

  def palues(self):
    return self[self.peys()]

  def pitems(self):
    return self.palues().root()

  def qj(self, *a, **kw):
    return qj(self, _depth=2, *a, **kw)


pict = pdict


################################################################################
################################################################################
################################################################################
# defaultpdict class
################################################################################
################################################################################
################################################################################
class defaultpdict(defaultdict):
  """defaultdict subclass where everything is automatically a property.

  Use with dot notation or subscript notation:
  ```
    p = defaultpdict()
    p.foo = 1
    assert p['foo'] == 1
  ```

  List subscripts also work and return a plist of the corresponding keys:
  ```
    p = defaultpdict(foo=1, bar=2)
    assert p[['foo', 'bar']].aslist() == [1, 2]
  ```

  Setting with a list subscript also works, using a single element or a matching
  list for the values:
  ```
    p = defaultpdict()
    p[['foo', 'bar']] = 1
    assert p[['foo', 'bar']].aslist() == [1, 1]
    p[['foo', 'bar']] = [1, 2]
    assert p[['foo', 'bar']].aslist() == [1, 2]
  ```

  defaultpdict.update() returns self, rather than None, to support chaining:
  ```
    p = defaultpdict(foo=1, bar=2)
    p.update(bar=3).baz = 4
    assert p.bar == 3
    assert 'baz' in p.keys()
  ```

  Set the desired defualt constructor as normal to avoid having to construct
  individual values:
  ```
    p = defaultpdict(int)
    assert p.foo == 0
  ```

  Nested defaultpdicts make nice lightweight objects:
  ```
    p = defaultpdict(lambda: defaultpdict(list))
    p.foo = 1
    p.stats.bar.append(2)
    assert p['foo'] == 1
    assert p.stats.bar == [2]
  ```
  """

  def __init__(self, *a, **kw):
    defaultdict.__init__(self, *a, **kw)

  def __getattr__(self, name):
    if name.startswith('_'):
      return defaultdict.__getattribute__(self, name)
    if name == '*':
      return plist([self[k] for k in self])
    return self[name]

  def __setattr__(self, name, value):
    self[name] = value

  def __getitem__(self, key):
    if isinstance(key, list):
      return plist([self[k] for k in key], root=plist([KeyValue(k, self[k]) for k in key]))
    else:
      return defaultdict.__getitem__(self, key)

  def __setitem__(self, key, value):
    if isinstance(key, list):
      value = _ensure_len(len(key), value)
      for k, v in zip(key, value):
        defaultdict.__setitem__(self, k, v)
    else:
      defaultdict.__setitem__(self, key, value)
    return self

  def __str__(self):
    delim = ', ' if len(self) < 8 else ',\n '
    s = delim.join('%s: %s' % (repr(k), repr(self[k])) for k in self.peys())
    return '{' + s + '}'

  __repr__ = __str__

  def update(self, *a, **kw):
    defaultdict.update(self, *a, **kw)
    return self

  def copy(self):
    return defaultdict.copy(self)

  def peys(self):
    return plist(sorted(self.keys()))

  def palues(self):
    return self[self.peys()]

  def pitems(self):
    return self.palues().root()

  def qj(self, *a, **kw):
    return qj(self, _depth=2, *a, **kw)

defaultpict = defaultpdict


################################################################################
################################################################################
################################################################################
# pset class
################################################################################
################################################################################
################################################################################
class pset(set):
  """Placeholder set subclass. Not yet implemented."""
  pass


pet = pset


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
    """plist-compatible comparison operator. Note: comparisons filter plists.

    plist comparators can filter on leaf values:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    zero_bars = foo.bar == 0
      => [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]
    nonzero_bars = foo.bar != 0
      => [{'foo': 1, 'bar': 1}]
    ```

    They can also filter on other plists so long as the structures are
    compatible:
    ```
    foo == zero_bars
      => [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]
    foo.foo > foo.bar
      => [{'foo': 2, 'bar': 0}]
    ```

    The same is true when comparing against lists with compatible structure:
    ```
    foo.foo == [0, 1, 3]
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1}]
    ```

    This all generalizes naturally to plists that have been grouped:
    ```
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    nonzero_foo_by_bar_foo = foo_by_bar_foo.bar > 0
      => [[[],
           []],
          [[{'bar': 1, 'foo': 1}]]]
    zero_foo_by_bar_foo = foo_by_bar_foo.foo != nonzero_foo_by_bar_foo.foo
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[]]]
    foo_by_bar_foo.foo == [[[0], [3]], [[1]]]
      => [[[{'foo': 0, 'bar': 0}],
           []],
          [[{'foo': 1, 'bar': 1}]]]
    ```

    Lists with incompatible structure are compared to `self` one-at-a-time,
    resulting in set-like filtering where the two sets are merged with an 'or':
    ```
    foo.foo == [0, 1, 3, 4]
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1}]
    foo_by_bar_foo.foo == [0, 1, 3, 4]
      => [[[{'foo': 0, 'bar': 0}],
           []],
          [[{'foo': 1, 'bar': 1}]]]
    ```

    When comparing against an empty list, `==` always returns an empty list, but
    all other comparisons return `self`:
    ```
    foo.foo == []
      => []
    foo.foo < []
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    foo_by_bar_foo == nonzero_foo_by_bar_foo
      => [[[],
           []],
          [[{'foo': 1, 'bar': 1}]]]
    foo_by_bar_foo.foo > nonzero_foo_by_bar_foo.foo
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[]]]
    ```

    Args:
      self: plist object.
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
  """Builds a plist logical operation.

  Args:
    op: Logical operation, such as operator.__and__.

  Returns:
    logical_op: The logical operation function.
  """
  def logical_op(self, other):
    """plist-compatible logical operation; performs a set operation on its args.

    Args:
      self: plist object.
      other: Object to perform the logical operation with.

    Returns:
      A new plist, merging `self` and other according to the operation provided
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
    """plist-compatible binary operation; applied element-wise to its args.

    Args:
      self: plist object.
      other: Object to perform the binary operation with.

    Returns:
      A new plist, where each element of `self` had the operation passed to
      `_build_binary_op` applied to it and `other`, or the corresponding element
      of `other`, if the lengths of `self` and `other` match.
    """
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([op(x, o) for x, o in zip(self, other)], root=self.__root__)
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
    op: Unary operation, such as operator.__not__.

  Returns:
    unary_op: The unary operation function.
  """
  def unary_op(self):
    """plist-compatible unary operation; applied element-wise to its args.

    Args:
      self: plist object.

    Returns:
      A new plist, where each element of `self` had the operation passed to
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
    _pattr: Bound attribute found by a __getattribute__ or getattr call.
    *_pargs: Arguments passed directly to the attribute.
    **_pkwargs: Keyword arguments passed directly to the attribute, except
                `pepth` and `call_pepth`, which are removed.
                `pepth` tracks the desired depth in the plist of the
                attribute. When `pepth == 0`, the attribute is called or
                returned (for non-callable attributes).
                `call_pepth` tracks the actual depth the call occurs at. It is
                only passed on to a known list of plist methods that need it
                in order to correctly handle stack frames between the original
                caller and the final call.

  Returns:
    Either the value of the attribute, if the attribute is a known
    non-callable attribute, or the value of calling the attribute with the
    provided arguments.
  """
  pepth = _pkwargs.pop('pepth', 0)
  call_pepth = _pkwargs.pop('call_pepth', 0)
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
      return plist([_call_attr(x,
                               _pname,
                               attrs[i],
                               pepth=pepth - 1,
                               call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA,
                               *[a[i] for a in pargs],
                               **{k: v[i] for k, v in pkwargs.items()})
                    for i, x in enumerate(_pobj)],
                   root=_pobj.__root__)
    except Exception as e:
      if pepth > 0:
        raise e

  if _pname in ['qj', 'me']:
    result = _pattr(call_pepth=call_pepth, *_pargs, **_pkwargs)
  elif _pname in NONCALLABLE_ATTRS:
    return _pattr
  else:
    result = _pattr(*_pargs, **_pkwargs)

  if result is None and isinstance(_pobj, plist):
    return _pobj
  return result


def _ensure_len(length, x, strict=False):
  """Convert x to a list of length `length` if necessary and return it.

  This function is the core of plist 'deepcasting', which is conceptually
  similar to 'broadcasting' in numpy and tensorflow, but is intentionally much
  more permissive. Deepcasting relies on the fact that most functions will
  crash if they receive a list when they were expecting a scalar value. Allowing
  the called function to crash, rather than crashing in plist, allows plist to
  be optimistic, and avoids plist having to guess how a user-supplied function
  is meant to be called.

  Args:
    length: int.
    x: object to convert.
    strict: Boolean. If True, only plists are returned without being wrapped. Lists
            and other iterables of the correct length are still returned wrapped in
            a new list of the correct length. Defaults to False, which means that
            lists and other iterables of the correct length are returned unchanged.

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

    Args:
      name: Name of the attribute.

    Returns:
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

    Raises:
      AttributeError: If `name` is not found on self or the elements of self.
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
    """Delegates to __getitem__ for compatibility with python 2.7."""
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
    """Delegates to __setitem__ for compatibility with python 2.7."""
    if self.__pepth__ != 0:
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
    """Delegates to __delitem__ for compatibility with python 2.7."""
    if self.__pepth__ != 0:
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

    Args:
      *args: The arguments to apply to the callables in self.
      **kwargs: The keyword arguments to apply to the callables in self.
                pepth and call_pepth are updated before calling the callables.

    Returns:
      A new plist with the return values of calling each callable in self.
    """
    pepth = kwargs.pop('pepth', self.__pepth__)
    self.__pepth__ = 0
    call_pepth = kwargs.pop('call_pepth', 0)
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

    return plist([x(*[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

  ##############################################################################
  # __contains__
  ##############################################################################
  def __contains__(self, other):
    return list.__contains__(self, other)

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
    """Allow the use of plists in `with` statements."""
    return plist([x.__enter__() for x in self], root=self.__root__)

  def __exit__(self, exc_type, exc_value, traceback):
    """Allow the use of plists in `with` statements."""
    return plist([x.__exit__(exc_type, exc_value, traceback) for x in self], root=self.__root__).all(bool)

  ##############################################################################
  ##############################################################################
  ##############################################################################
  # Public methods.
  ##############################################################################
  ##############################################################################
  ##############################################################################

  def _(self):
    self.__pepth__ = -1
    return self

  ##############################################################################
  # __root__ pointer management.
  ##############################################################################
  def root(self):
    """Returns the root of the plist.

    Most plist methods maintain the root pointer so that it is possible to
    return to the plist from which later results are generated.
    """
    return self.__root__

  def uproot(self):
    """Sets the root to `self` so future `root()` calls return this plist."""
    self.__root__ = self
    return self

  ##############################################################################
  # Conversion methods.
  ##############################################################################
  def aslist(self):
    """Recursively convert all nested plists from self to lists, inclusive."""
    try:
      return [x.aslist() for x in self]
    except Exception:
      pass
    return [x for x in self]

  def astuple(self):
    """Recursively convert all nested plists from self to tuples, inclusive."""
    try:
      return tuple([x.astuple() for x in self])
    except Exception:
      pass
    return tuple([x for x in self])

  def aspset(self):
    try:
      return pset([x.aspset() for x in self])
    except Exception:
      pass
    return pset([x for x in self])

  def aspdict(self):
    try:
      return plist([x.aspdict() for x in self], root=self.__root__)
    except Exception:
      pass
    return self.pdict()

  def np(self, *args, **kwargs):
    """Converts the elements of self to numpy arrays, forwarding passed args."""
    return plist([np.array(x, *args, **kwargs) for x in self], root=self.__root__)

  def pd(self, *args, **kwargs):
    """Converts self into a pandas DataFrame, forwarding passed args."""
    return pd.DataFrame.from_records(self.aslist(), *args, **kwargs)

  def pdict(self, *args, **kwargs):
    if self is self.__root__:
      return pdict({k: v for k, v in self}).update(*args, **kwargs)
    if self.__root__.all(isinstance, KeyValue):
      return pdict({k: v for k, v in zip(self.__root__.key, self)}).update(*args, **kwargs)
    return pdict({k: v for k, v in zip(self.__root__, self)}).update(*args, **kwargs)

  def pset(self):
    """Converts the elements of self into pset objects."""
    return plist([pset(x) for x in self], root=self.__root__)

  def pstr(self):
    """Returns a plist with leaf elements converted to strings."""
    try:
      return plist([x.pstr() for x in self], root=self.__root__)
    except Exception:
      return plist([str(x) for x in self], root=self.__root__)

  ##############################################################################
  # Shortcutting boolean test methods.
  ##############################################################################
  def all(self, *args, **kwargs):
    """Returns self if args[0] evaluates to True for all elements of self.

    Shortcuts if args[0] ever evaluates to False.
    If args are not passed, the function evaluated is `bool`.

    Args:
      *args: Optional. If present, the first entry must be a function to evaluate.
             All other args are passed through to that function. If absent, the
             function is set to bool.
      **kwargs: Passed through to the function specified in *args.

    Returns:
      `self` or an empty plist (which evaluates to False).
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
    """Returns self if args[0] evaluates to True for any element of self.

    Shortcuts as soon as args[0] evaluates to True.
    If args are not passed, the function evaluated is `bool`.

    Args:
      *args: Optional. If present, the first entry must be a function to evaluate.
             All other args are passed through to that function. If absent, the
             function is set to bool.
      **kwargs: Passed through to func.

    Returns:
      `self` or an empty plist (which evaluates to False).
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
    """Returns self if args[0] evaluates to False for all elements.

    Shortcuts if args[0] ever evaluates to evaluates to True.
    If args are not passed, the function evaluated is `bool`.

    Args:
      *args: Optional. If present, the first entry must be a function to evaluate.
             All other args are passed through to that function. If absent, the
             function is set to bool.
      **kwargs: Passed through to func.

    Returns:
      `self` or an empty plist (which evaluates to False).
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
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    zero_bars = foo.bar == 0
      => [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]
    foo == zero_bars
      => [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]
    foo.pequal(zero_bars)
      => False
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

    Args:
      func: callable or string name of method in plist class.
      *args: Arguments to pass to func.
      **kwargs: Keyword arguments to pass to `func`, after extracting:
                `paslist`: Boolean (default `False`). If `True`, converts
                           elements of self to list using `plist.aslist()`
                           before passing them to `func`, and reconverts the
                           result of each call to a plist. Note that this does
                           not guarantee that the returned plist has the same
                           shape as `self`, as plist.aslist() recursively
                           converts all contained plists to lists, but `func`
                           might return any arbitrary result, so the same
                           conversion cannot be inverted automatically.
                `psplat`: Boolean (default `False`). If `True`, expands the
                          arguments provided by `self` with the `*` operator
                          (sometimes called the 'splat' operator).

    Returns:
      plist resulting from applying func to each element of self.
    """
    paslist = kwargs.pop('paslist', False)
    psplat = kwargs.pop('psplat', False)
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

    if paslist:
      if psplat:
        return plist([plist(funcs[i](*x.aslist() + [a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}), root=x.__root__) for i, x in enumerate(self)], root=self.__root__)
      return plist([plist(funcs[i](x.aslist(), *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}), root=x.__root__) for i, x in enumerate(self)], root=self.__root__)
    else:
      if psplat:
        return plist([funcs[i](*list(x) + [a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
      return plist([funcs[i](x, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

  def qj(self, *args, **kwargs):
    """Applies logging function qj to self for easy in-chain logging.

    Args:
      *args: Arguments to pass to qj.
      **kwargs: Keyword arguments to pass to qj.

    Returns:
      self
    """
    call_pepth = kwargs.pop('call_pepth', 0)
    return qj(self, _depth=4 + call_pepth, *args, **kwargs)

  ##############################################################################
  # Grouping and sorting methods.
  ##############################################################################
  def groupby(self):
    """Group self.root() by the values in self.

    Given a plist:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    foo_by_bar = foo.bar.groupby()
      => [[{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}],
          [{'foo': 1, 'bar': 1}]]
    ```
    Note that foo_by_bar now has two nested plists. The first inner plist has
    the two pdicts where `foo.bar == 0`. The second inner plist has the
    remaining pdict where `foo.bar == 1`.

    Calling groupby again:
    ```
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    ```
    Now foo_by_bar_foo has two nested layers of inner plists. The outer nest
    groups the values by `bar`, and the inner nest groups them by `foo`.

    groupby always operates with leaf children of the plist, and it always adds
    new groups as subgroups of the current innermost group.

    Grouping relies on the values being hashable. If, for some reason, you need
    to group by a non-hashable value, you should convert it to a hashable
    representation first, for example using `plist.pstr()` or `plist.apply(id)`:
    ```
    foo = plist([{'bar': [1, 2, 3]}, {'bar': [1, 2, 3]}])
    foo_by_bar_crash = foo.bar.groupby()  # CRASHES!
    foo_by_bar_pstr = foo.bar.pstr().groupby()
      => [[{'bar': [1, 2, 3]},
           {'bar': [1, 2, 3]}]]
    foo_by_bar_id = foo.bar.apply(id).groupby()
      => [[{'bar': [1, 2, 3]}],
          [{'bar': [1, 2, 3]}]]
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

  def join(self):
    """Adds and returns an outer plist around self.

    `join` is useful when you wish to call a function on the top-level plist,
    but you don't want to stop your call chain:
    ```
    foo = plist([{'bar': [1, 2, 3]}, {'bar': [4, 5, 6]}])
      => [{'bar': [1, 2, 3]},
          {'bar': [4, 5, 6]}]
    arr1 = np.array(foo.bar.pstr().groupby().bar)
      => array([[[1, 2, 3],
                 [4, 5, 6]]])
    arr2 = foo.bar.pstr().groupby().bar.np()
      => [array([[1, 2, 3],
                 [4, 5, 6]])]
    arr3 = foo.bar.pstr().groupby().bar.join().np()
      => [array([[[1, 2, 3],
                  [4, 5, 6]]])]
    assert arr1 == arr2[0]  # FALSE!
    assert arr1 == arr3[0]  # TRUE!
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
    """Sorts self and self.root() in-place and returns self.

    `sortby` and `groupby` work together nicely to create sorted, nested plists.
    Note that `sortby` modifies and returns self, whereas `groupby` returns a
    new plist with a new root. This is because `sortby` doesn't change the
    structure of the plist, only the order of its (or its children's) elements.

    A basic sort:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    bar_sorted = foo.bar.sortby()
      => [0, 0, 1]
    foo_sorted_by_bar = bar_sorted.root()
      => [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0},
          {'foo': 1, 'bar': 1}]
    ```

    Sorting with groups works in the same way -- the sort is applied to each
    group of `self`:
    ```
    foo_by_bar = foo.bar.groupby()
      => [[{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}],
          [{'foo': 1, 'bar': 1}]]
    bar_by_bar_sorted = foo_by_bar.bar.sortby(reverse=True)
      => [[1], [0, 0]]
    foo_by_bar_sorted = bar_by_bar_sorted.root()
      => [[{'foo': 1, 'bar': 1}],
          [{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}]]
    ```

    Args:
      key: Key function to pass to `sorted`. Defaults to the identity function.
           See the python documentation for `sorted` for more information.
      reverse: Boolean specifying whether to sort in reverse order or not.

    Returns:
      self, sorted.
    """
    key = key or (lambda x: x)
    sorted_inds = [i for i, _ in sorted(enumerate(self), key=lambda x: key(x[1]), reverse=reverse)]
    self.__root__[:] = self.__root__[sorted_inds]
    if self is not self.__root__:
      self[:] = self[sorted_inds]
    return self

  def ungroup(self, r=1, s=None):
    """Inverts the last grouping operation applied and returns a new plist.

    Args:
      r: Integer value for the number of groups to remove. If `r == 0`, no
         groups are removed. If it is positive, that many groups must be
         removed, or `upgroup` throws a `ValueError`. If `r < 0`, all groups in
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

  ##############################################################################
  # Additional filtering methods.
  ##############################################################################
  def nonempty(self, r=0):
    """Returns a new plist with empty sublists removed.

    `nonempty` is useful in combination with grouping and filtering:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    foo_by_bar = foo.bar.groupby()
      => [[{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}],
          [{'foo': 1, 'bar': 1}]]
    filtered = foo_by_bar.foo != 1
      => [[{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}],
          []]
    filtered_nonempty = filtered.nonempty()
      => [[{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}]]
    ```

    If the plist is deep, multiple levels of empty sublists can be removed at
    the same time:
    ```
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    filtered = foo_by_bar_foo.foo != 1
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[]]]
    filtered_nonempty_0 = filtered.nonempty()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[]]]
    filtered_nonempty_1 = filtered.nonempty(1)
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]]]
    filtered_nonempty_n1 = filtered.nonempty(-1)
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]]]
    ```
    Note that `filtered_nonempty_0` is identical to `filteed`, since there are
    no empty sublists at the top level. In this example, `filtered_nonempty_1`
    and `filtered_nonempty_n1` give the same result -- the deepest empty sublist
    is removed, and then the next deepest empty sublist is removed.

    It is also possible to remove empty sublists only at deeper levels, using
    the two ways to call functions on sublists -- passing `pepth` and adding `_`
    to the method name:
    ```
    filtered_nonempty_p1 = filtered.nonempty(pepth=1)
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          []]
    filtered_nonempty_u1 = filtered.nonempty_()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          []]
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
    return plist([x for x in new_plist if len(x)])

  def preduce_eq(self):
    """Returns a new plist with only a single element of each value in self.

    `preduce_eq` reduces the values of the groups of self using an equality
    check:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    reduced = foo.bar.preduce_eq()
      => [0, 1]
    reduced.root()
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1}]
    ```

    Grouped plists
    ```
    foo_by_bar = foo.bar.groupby()
      => [[{'foo': 0, 'bar': 0},
           {'foo': 2, 'bar': 0}],
          [{'foo': 1, 'bar': 1}]]
    reduced = foo_by_bar.bar.preduce_eq()
      => [[0], [1]]
    reduced.root()
      => [[{'foo': 0, 'bar': 0}],
          [{'foo': 1, 'bar': 1}]]
    ```

    The equality check respects the subgroups of self:
    ```
    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    reduced_no_effect = foo_by_bar_foo.bar.preduce_eq()
      => [[[0], [0]], [[1]]]
    reduced_no_effect.root()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    ```

    As with `plist.groupby`, `preduce_eq` relies on the values being hashable.
    If, for some reason, you need to reduce by a non-hashable value, you should
    convert it to a hashable representation first, for example using
    `plist.pstr()` or `plist.apply(id)`:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=0, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 0, 'bar': 0}]
    reduced_crash = foo.preduce_eq()  # CRASHES!
    reduced_pstr = foo.pstr().preduce_eq()
      => ["{'foo': 0, 'bar': 0}",
          "{'foo': 1, 'bar': 1}"]
    reduced_pstr.root()
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1}]
    reduced_id = foo.apply(id).preduce_eq()
      => [4689112496, 4689260040, 4689258368]
    reduced_id.root()
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 0, 'bar': 0}]
    ```
    In this case, since each of the elements of `foo` are unique pdicts,
    reducing by `plist.apply(id)` has no useful effect, but if there had been
    any duplicates in the elements of `foo`, they would have been removed.

    Returns:
      New plist with a new `root` where there is only one example of each value
      in each sublist. The corresponding `root` element is the first element in
      `self.root()` that has that value.
    """
    try:
      return plist([x.preduce_eq() for x in self], root=self.__root__)
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

  puniq = preduce_eq

  def remix(self, *args, **kwargs):
    """Returns a new plist of pdicts based on selected data from self.

    `remix` allows you to easily restructure your data into a manageable form:
    ```
    foo = plist([{'foo': 0, 'bar': {'baz': 13, 'bam': 0, 'bin': 'not'}},
                 {'foo': 1, 'bar': {'baz': 42, 'bam': 1, 'bin': 'good'}},
                 {'foo': 2, 'bar': {'baz': -9, 'bam': 0, 'bin': 'data'}}])
    rmx = foo.remix('foo', baz=foo.bar.baz)
      => [{'foo': 0, 'baz': 13},
          {'foo': 1, 'baz': 42},
          {'foo': 2, 'baz': -9}]
    ```
    Note that `rmx.baz` gets its values from `foo.bar.baz` in a natural manner.

    If `remix` is called on a grouped plist, the result is still a flat plist
    of flat pdicts, but the values in the pdicts are themselves pdicts:
    ```
    foo_by_bam = foo.bar.bam.groupby()
      => [[{'foo': 0, 'bar': {'bam': 0, 'baz': 13, 'bin': 'not'}},
           {'foo': 2, 'bar': {'bam': 0, 'baz': -9, 'bin': 'data'}}],
          [{'foo': 1, 'bar': {'bam': 1, 'baz': 42, 'bin': 'good'}}]]
    rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz)
      => [{'foo': [0, 2], 'baz': [13, -9]},
          {'foo': [1],    'baz': [42]}]
    ```

    This behavior can be useful when integrating with pandas, for example:
    ```
    df = rmx_by_bam.pd()
      =>         baz     foo
         0  [13, -9]  [0, 2]
         1      [42]     [1]
    ```

    If you instead want `remix` to return grouped pdicts, just pass `pepth=-1`
    to have it execute on the deepest plists, as with any other call to a plist:
    ```
    rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz, pepth=-1)
      => [[{'foo': 0, 'baz': 13},
           {'foo': 2, 'baz': -9}],
          [{'foo': 1, 'baz': 42}]]
    ```

    Args:
      *args: List of property names of items in `self` to include in the remix.
      **kwargs: Key/value pairs where the key will be a new property on items in
                the remix and the value is a deepcast and set to that key.

    Returns:
      Flat plist of flat pdicts based on data from self and the passed arguments
      and keyword arguments.
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
    """Returns a plist of the recursive depth of each leaf element, from 0.

    `pdepth` returns a plist of the same plist structure as self:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    depth = foo.pdepth()
      => [0]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    depth = foo_by_bar_foo.pdepth()
      => [[[2], [2]], [[2]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    filtered.pdepth()
      => [[[2], [2]], [[]]]
    ```

    Since the depth values are always equal or empty in well-formed plists, it
    is sometimes more convenient to get the depth as a scalar value. Pass a True
    value to the first parameter (`s` for 'scalar'):
    ```
    depth = foo.pdepth(s=1)
      => 0
    depth = foo_by_bar_foo.pdepth(1)
      => 2
    depth = filtered.pdepth(True)
      => 2
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
    """Returns a plist of the length of a recursively-selected layer of self.

    `plen` returns a plist of the same depth as self, up to `r`:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    length = foo.plen()
      => [3]
    length_r1 = foo.plen(1)
      => [3]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    length = foo_by_bar_foo.plen()
      => [2]
    length = foo_by_bar_foo.plen(r=1)
      => [[3]]
    length = foo_by_bar_foo.plen(2)
      => [[[3]]]
    length = foo_by_bar_foo.plen(-1)
      => [[[3]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    filtered.plen()
      => [2]
    filtered.plen(-1)
      => [[[2]]]
    ```

    Since the depth values are always equal or empty in well-formed plists, it
    is sometimes more convenient to get the depth as a scalar value. Pass a True
    value to the first parameter (`s` for 'scalar'):
    ```
    length = foo.plen(s=1)
      => 3
    length = foo_by_bar_foo.plen(r=2, s=1)
      => 3
    length = filtered.plen(-1, s=True)
      => 2
    ```

    Args:
      r: Target recursion depth. Defaults to 0. Set to -1 to recurse as deep as
         possible.
      s: Boolean that controls whether a scalar is returned (when `True`) or a
         plist of the same depth as self (when `False`, the default).

    Returns:
      plist whose depth equals the requested recursion depth (or less, if
      `r > self.pdepth()`), containing a single value which is the number of
      plist elements at that depth, or that value as a scalar if `s` is `True`.
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
    """Returns a plist of the same structure as self, filled with leaf lengths.

    `pshape` returns a plist of the same structure as self:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    shape = foo.pshape()
      => [3]

    foo_by_bar = foo.bar.groupby()
      => [[{'bar': 0, 'foo': 0},
           {'bar': 0, 'foo': 2}],
          [{'bar': 1, 'foo': 1}]]
    shape = foo_by_bar.pshape()
      => [[2], [1]]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    shape = foo_by_bar_foo.pshape()
      => [[[1], [1]], [[1]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    shape = filtered.pshape()
      => [[[1], [1]], [[]]]
    ```

    Returns:
      plist of the same structure as self, where each leaf plist has a single
      element, which is the length of the corresponding leaf plist in `self`.
    """
    try:
      return plist([x.pshape() for x in self], root=self.__root__)
    except Exception:
      return plist([len(self)], root=self.__root__)

  def pstructure(self):
    """Returns a list of the number of elements in each layer of self.

    Gives a snapshot view of the structure of `self`. The length of the returned
    list is the depth of `self`. Each value in the list is the result of calling
    `self.plen(r)`, where `r` ranges from 0 to `self.pdepth()`. `plen(r)` gives
    the sum of the lengths of all plists at layer `r`.
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    structure = foo.pstructure()
      => [3]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    structure = foo_by_bar_foo.pstructure()
      => [2, 3, 3]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    structure = filtered.pstructure()
      => [2, 3, 2]
    ```

    Returns:
      A list (not a plist) of `self.pdepth()` integers, where each integer is
      the number of elements in all plists at that layer, 0-indexed according to
      depth.
    """
    s = []
    for r in range(self.pdepth(True) + 1):
      s.extend(self.plen(r).ungroup(-1))
    return plist(s, root=self.__root__)

  # Fill with different values.
  def lfill(self, v=0, s=None):
    """Returns a list with the structure of `self` filled in order from `v`.

    Identical to `plist.pfill()`, but returns a list instead of a plist.
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    filled = foo.lfill()
      => [0, 1, 2]
    filled = foo.lfill(-7)
      => [-7, -6, -5]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    filled = foo_by_bar_foo.lfill()
      => [[[0], [1]], [[2]]]
    filled = foo_by_bar_foo.lfill_()
      => [[[0], [1]], [[0]]]
    filled = foo_by_bar_foo.lfill(pepth=2)
      => [[[0], [0]], [[0]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    filled = filtered.lfill(3)
      => [[[3], [4]], [[]]]
    ```

    Args:
      v: Integer. The value to start filling from. Defaults to 0.
      s: Successor object. Do not pass -- used to track the count of calls
         across the recursive traversal of `self`.

    Returns:
      A list (not a plist) of possibly nested plists where each leaf element is
      an integer, starting with the value of `v` in the 'top left' element of
      the structure.
    """
    s = _successor(v - 1) if s is None else s
    try:
      return [x.lfill(s=s) for x in self]
    except Exception:
      return [s.s() for _ in range(len(self))]

  def pfill(self, v=0, s=None):
    """Returns a plist with the structure of `self` filled in order from `v`.

    Identical to `plist.lfill()`, but returns a plist instead of a list.
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    filled = foo.pfill()
      => [0, 1, 2]
    filled = foo.pfill(-7)
      => [-7, -6, -5]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    filled = foo_by_bar_foo.pfill()
      => [[[0], [1]], [[2]]]
    filled = foo_by_bar_foo.pfill_()
      => [[[0], [1]], [[0]]]
    filled = foo_by_bar_foo.pfill(pepth=2)
      => [[[0], [0]], [[0]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    filled = filtered.pfill(3)
      => [[[3], [4]], [[]]]
    ```

    Args:
      v: Integer. The value to start filling from. Defaults to 0.
      s: Successor object. Do not pass -- used to track the count of calls
         across the recursive traversal of `self`.

    Returns:
      A plist of possibly nested plists where each leaf element is an integer,
      starting with the value of `v` in the 'top left' element of the structure.
    """
    s = _successor(v - 1) if s is None else s
    try:
      return plist([x.pfill(s=s) for x in self], root=self.__root__)
    except Exception:
      return plist([s.s() for _ in range(len(self))], root=self.__root__)

  def pleft(self):
    """Returns a plist with the structure of `self` filled `plen(-1)` to 0.

    Convenience method identical to `-self.pfill(1) + self.plen(-1, s=True)`:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    remaining = foo.pleft()
      => [2, 1, 0]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    remaining = foo_by_bar_foo.pleft()
      => [[[2], [1]], [[0]]]
    remaining = foo_by_bar_foo.pleft_()
      => [[[1], [0]], [[0]]]
    remaining = foo_by_bar_foo.pleft(pepth=2)
      => [[[0], [0]], [[0]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    remaining = filtered.pleft()
      => [[[1], [0]], [[]]]
    ```
    This is useful for calling functions that have some global state that should
    change each time a new grouping is started, such as generating many plots
    from a single grouped plist using pyplot, where the function would need to
    call `plt.show()` after each group was completed:
    ```
    def plot(x, remaining):
      plt.plot(x)

      if remaining == 0:
        plt.show()

    by_bar_baz_bin.foo.apply(plot, by_bar_baz_bin.pleft(pepth=2), pepth=2)
    ```

    Returns:
      A plist of possibly nested plists where each leaf element is an integer,
      starting with `self.plen(-1)` in the 'top left' element of the structure
      and counting down to 0.
    """
    return -self.pfill(1) + self.plen(-1, s=True)

  def values_like(self, value=0):
    """Returns a plist with the structure of `self` filled with `value`.

    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    ones = foo.values_like(1)
      => [1, 1, 1]

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
      => [[[{'foo': 0, 'bar': 0}],
           [{'foo': 2, 'bar': 0}]],
          [[{'foo': 1, 'bar': 1}]]]
    strings = foo_by_bar_foo.values_like('foo')
      => [[['foo'], ['foo']], [['foo']]]
    all_the_same_dict = foo_by_bar_foo.values_like({}, pepth=2)
      => [[[{}], [{}]], [[{}]]]
    all_the_same_dict.ungroup(-1)[0].update(foo=1)
      => None
    all_the_same_dict
      => [[[{'foo': 1}], [{'foo': 1}]], [[{'foo': 1}]]]

    filtered = foo_by_bar_foo.bar == 0
      => [[[{'bar': 0, 'foo': 0}],
           [{'bar': 0, 'foo': 2}]],
          [[]]]
    tuples = filtered.values_like((1, 2, 3))
      => [[[(1, 2, 3)], [(1, 2, 3)]], [[]]]
    ```
    Note the example above that filling with a mutable object like a dict gives
    a plist filled that single object, which might be surprising, but is the
    same as other common python idioms, such as:
    ```
    all_the_same_dict = [{}] * 3
      => [{}, {}, {}]
    all_the_same_dict[0].update(foo=1)
      => None
    all_the_same_dict
      => [{'foo': 1}, {'foo': 1}, {'foo': 1}]
    ```

    Args:
      value: Value to fill the returned plist with. Can by any python object.

    Returns:
      A plist with the structure of `self` filled with `value`.
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
    the data in the plist for a future call to `apply` or some other call. It
    attempts to add the current plist to the caller's context, either as a
    local variable, or as a global (module-level) variable. Because it modifies
    the caller's frame, it is not recommended for production code, but can be
    qutie useful in jupyter notebooks during exploration of datasets.

    Using `me` with a local variable requires that the variable already exist in
    the local context, and that it be a plist:
    ```
    me = plist()
    foo.bar.groupby().baz.sortby_().me().groupby().apply_(plt.plot, me)
    ```

    The same can work with a name of your choice:
    ```
    baz = plist()
    foo.bar.groupby().baz.sortby_().me('baz').groupby().apply_(plt.plot, baz)
    ```

    You can pass the plist you want to use instead:
    ```
    me2 = plist()
    foo.bar.groupby().baz.sortby_().me(me2).groupby().apply_(plt.plot, me2)
    ```

    If there isn't a local variable of that name, `me()` will put the plist into
    the caller's `globals()` dict under the requested name. The following both
    work if there are no local or global variables named `me` or `baz`:
    ```
    foo.bar.groupby().baz.sortby_().me().groupby().apply_(plt.plot, me)
    foo.bar.groupby().baz.sortby_().me('baz').groupby().apply_(plt.plot, baz)
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
                  caller's local variables, but does not evaluate to a plist.
      ValueError: If something other than a string or a plist is passed to
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
    """Stores `self` into a plist of tuples that gets extended with each call.

    `pand` is meant to facilitate building up tuples of values to be sent as
    a single block to a chained call to `apply`, or as `*args` when calling
    `plist.apply(psplat=True)`. The name is `pand` to evoke conjunction: the
    caller wants a plist with this *and* this *and* this.

    `pand` stores a variable in the caller's frame that isn't visible to the
    caller, but is visible to future calls to `pand` due to how `locals()`
    works.

    Basic usage might look like:
    ```
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      => [{'foo': 0, 'bar': 0},
          {'foo': 1, 'bar': 1},
          {'foo': 2, 'bar': 0}]
    foo.baz = 3 * foo.foo + foo.bar
      => [{'foo': 0, 'bar': 0, 'baz': 0},
          {'foo': 1, 'bar': 1, 'baz': 4},
          {'foo': 2, 'bar': 0, 'baz': 6}]
    (foo.bar.groupby().baz.groupby().foo.pand().root().bar.pand().ungroup()
        .apply_(qj, '(foo, bar)'))
      => [[[(0, 0)],
           [(2, 0)]],
          [[(1, 1)]]]
      Logs:
        qj: <pstar> apply: (foo, bar) <1249>: (0, 0)
        qj: <pstar> apply: (foo, bar) <1249>: (2, 0)
        qj: <pstar> apply: (foo, bar) <1249>: (1, 1)
    ```

    The same construction can be used with methods that expect the arguments
    individually, requiring the tuple to be expanded:
    ```
    (foo.bar.groupby().baz.groupby().foo.pand().root().bar.pstr().pand()
        .ungroup().apply_(qj, psplat=True))
    ```

    Building multiple tuples in the same context requires passing `name` to keep
    them separate:
    ```
    (foo.bar.groupby().baz.groupby().me().foo.pand().root().bar.pand().ungroup()
        .apply_(qj,
                me.foo.pand('strs').root().bar.pand('strs').ungroup().pstr()))
      => [[(0, 0),
           (2, 0)],
          [(1, 1)]]
      Logs:
        qj: <pstar> apply: (0, 0) <1249>: (0, 0)
        qj: <pstar> apply: (2, 0) <1249>: (2, 0)
        qj: <pstar> apply: (1, 1) <1249>: (1, 1)
    ```
    Note that the construction above is hard to understand, and probably
    shouldn't be used.

    Args:
      name: String naming an available variable in the caller's context. Should
            only be passed if the calling frame needs to create multiple
            different tuples. Defaults to '__plist_and_var__'. If a variable of
            the same name exists in the caller's context, `pand` will fail to
            write to it.
      call_pepth: Do not pass. Used by `plist.__call__` to keep track of how
                  many stack frames occur between the caller and `pand()`.

    Returns:
      The current plist of tuples, with `self` added.

    Raises:
      ValueError: If the variable named by `name` is already present in the
                  caller's frame and is not a plist, or has different `pshape()`
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


pist = plist


# pylint: enable=line-too-long,invalid-name,g-explicit-length-test
# pylint: enable=broad-except,g-long-lambda
