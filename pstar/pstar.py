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
"""pstar

Import with:
  from pstar import *
"""

import collections
from collections import defaultdict
import inspect
import operator
import os
import sys
import types

import numpy as np
import pandas as pd
from qj import qj


if sys.version_info[0] < 3:
  STRING_TYPES = types.StringTypes
  PLIST_CALL_ATTR_CALL_PEPTH_DELTA = 1
else:
  STRING_TYPES = str
  PLIST_CALL_ATTR_CALL_PEPTH_DELTA = 2

class pdict(dict):  # pylint: disable=invalid-name
  """Dict where everything is automatically a property."""

  def __init__(self, *a, **kw):
    dict.__init__(self, *a, **kw)
    self.__dict__ = self

  # TODO(iansf): FIGURE OUT IF WE NEED TO OVERRIDE EQUALITY!
  # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
  # def __cmp__(self, other):
  #   return self is other

  # __eq__ = __cmp__

  # def __ne__(self, other):
  #   return not self == other
  # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  # TODO(iansf): FIGURE OUT IF WE NEED TO OVERRIDE EQUALITY!

  def __getitem__(self, key):
    if isinstance(key, list):
      return plist([self[x] for x in key])
    else:
      return dict.__getitem__(self, key)
#       try:
#         return dict.__getitem__(self, key)
#       except KeyError:
#         try:
#           if hasattr(self, key):
#             return getattr(self, key)
#         except AttributeError:
#           raise KeyError('\'%s\' is neither a key nor an attribute in this \'%s\'' % (key, type(self)))


  def __setitem__(self, key, value):
    if isinstance(key, list) and not isinstance(value, STRING_TYPES) and hasattr(value, '__len__') and len(value) == len(key):
      for k, v in zip(key, value):
        dict.__setitem__(self, k, v)
    else:
      dict.__setitem__(self, key, value)

  def update(self, *a, **kw):
    dict.update(self, *a, **kw)
    return self

  def copy(self):
    return pdict(dict.copy(self))


pict = pdict


class defaultpdict(defaultdict):  # pylint: disable=invalid-name
  """Default dict where everything is automatically a property."""

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

  # TODO(iansf): FIGURE OUT IF WE NEED TO OVERRIDE EQUALITY!
  # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
  # def __cmp__(self, other):
  #   return self is other

  # __eq__ = __cmp__

  # def __ne__(self, other):
  #   return not self == other
  # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  # TODO(iansf): FIGURE OUT IF WE NEED TO OVERRIDE EQUALITY!

  def __str__(self):
    delim = ', ' if len(self) < 8 else ',\n '
    s = delim.join('%s: %s' % (repr(k), repr(self[k])) for k in sorted(self))
    return '{' + s + '}'

  __repr__ = __str__

  def __getitem__(self, key):
    if isinstance(key, list):
      return plist([self[x] for x in key])
    else:
      return defaultdict.__getitem__(self, key)
#       try:
#         return defaultdict.__getitem__(self, key)
#       except KeyError:
#         try:
#           if hasattr(self, key):
#             return getattr(self, key)
#         except AttributeError:
#           raise KeyError('\'%s\' is neither a key nor an attribute in this \'%s\'' % (key, type(self)))

  def __setitem__(self, key, value):
    if isinstance(key, list) and not isinstance(value, STRING_TYPES) and hasattr(value, '__len__') and len(value) == len(key):
      for k, v in zip(key, value):
        defaultdict.__setitem__(self, k, v)
    else:
      defaultdict.__setitem__(self, key, value)

  def update(self, *a, **kw):
    defaultdict.update(self, *a, **kw)
    return self

  def copy(self):
    return defaultpdict(defaultdict.copy(self))


defaultpict = defaultpdict


class pset(set):
  pass


pet = pset


dbg = 0


def _build_comparator(op, merge_op, shortcut):
  def comparator(self, other, return_inds=False):
    if self is other:
      return shortcut(self, return_inds)
    # qj((self, other), '(self, other)', b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = comparator(x, o, return_inds=True)
          inds.append(child_inds)
        elif op(x, o):
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = comparator(self, other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, comparator(self, o, return_inds=True), merge_op)
      # qj((inds, self, other), 'inds self %s other)' % op.__name__, b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = comparator(x, other, return_inds=True)
          inds.append(child_inds)
        elif op(x, other):
          inds.append(i)

    # qj(inds, 'inds %s self: %s other: %s' % (op.__name__, 'str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds %s self: %s other: %s' % (op.__name__, 'str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return %s self: %s other: %s' % (op.__name__, 'str(self)', 'str(other)'), b=0)

  return comparator


def _build_logical_op(op):
  def logical_op(self, other):
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
  def binary_op(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([op(x, o) for x, o in zip(self, other)], root=self.__root__)
    return plist([op(x, other) for x in self], root=self.__root__)

  return binary_op


def _build_binary_rop(op):
  def binary_rop(self, other):
    return plist([op(other, x) for x in self], root=self.__root__)

  return binary_rop


def _build_binary_ops(op, iop):
  return _build_binary_op(op), _build_binary_rop(op), _build_binary_op(iop)


def _build_unary_op(op):
  def unary_op(self):
    return plist([op(x) for x in self], root=self.__root__)

  return unary_op


class plist(list):  # pylint: disable=invalid-name
  """List where everything is automatically a property that is applied to its elements.  Guaranteed to surprise, if not delight."""

  def __init__(self, *args, **kwargs):
    depth = kwargs.pop('depth', 1)
    self.__root__ = kwargs.pop('root', self)
    if depth == 1:
      list.__init__(self, *args, **kwargs)
    else:
      # Don't pass root through when making nested plists, because that doesn't make any sense.
      plist.__init__(self, [plist(*args, depth=depth - 1, **kwargs)])

  def __getattribute__(self, name):
    if name == '__root__':
      return list.__getattribute__(self, name)
    if not name.endswith('___') and name.startswith('__') and name.endswith('__'):
      raise qj(AttributeError('\'%s\' objects cannot call reserved members of their elements: \'%s\'' % (type(self), name)), l=lambda _: self, b=0*dbg)
    # qj(self, name, b=dbg)
    try:
      return qj(plist.__getattr__(self, name), name, b=dbg)
    except AttributeError:
      # qj(self, 'caught AttributeError for %s' % name, b=dbg)
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
        return qj(plist.__getattr__(self, name[:-ending_unders], _pepth=ending_unders), name, b=dbg)
      except AttributeError:
        pass
      name = name[:-1]
    try:
      # qj(name, 'trying', b=0)
      return qj(
          plist([
            (qj(hasattr(*qj((x, name), 'calling hasattr', l=lambda y: (self, y[0], type(y[0])), b=dbg)), 'hasattr %s' % name, l=lambda _: (self, x, type(x)), b=dbg)
             and getattr(x, name))
            or x[name] for x in self],
            root=self.__root__)
          , name, b=dbg)
    except Exception as e:
      raise qj(AttributeError('\'%s\' object has no attribute \'%s\' (%s)' % (type(self), name, str(e))), l=lambda _: self, b=dbg)


  def __getattr__(self, name, _pepth=0):
    # qj(self, name, b=dbg * (not name.startswith('__')))
    attr = list.__getattribute__(self, name)

    def call_attr(self, attr, *args, **kwargs):
      pepth = kwargs.pop('pepth', 0)
      call_pepth = kwargs.pop('call_pepth', 0)
      if pepth != 0:
        if not isinstance(self, plist):
          raise Exception  # ('Attempting to call attr %s on object of type %s' % (name, type(self)))
        pargs = [_ensure_len(len(self), a) for a in args]
        pkwargs = {
            k: _ensure_len(len(self), v) for k, v in kwargs.items()
        }
        # qj(self, 'About to try calling attr %r (%s) at pepth %d' % (attr, name, pepth), b=dbg * (not name.startswith('__')))
        if pepth < 0:
          try:
            attrs = [list.__getattribute__(x, name) if isinstance(x, list) else getattr(x, name) for x in self]
            return plist([call_attr(x, attrs[i], pepth=pepth - 1, call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA, *[a[i] for a in pargs], **{k: v[i] for k, v in pkwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
          except Exception as e:
            # qj(self, 'caught %s calling attr %r (%s) at pepth %d:\n%r' % (type(e), attr, name, pepth, e), b=dbg * (not name.startswith('__')))
            pass
        else:
          attrs = [list.__getattribute__(x, name) if isinstance(x, list) else getattr(x, name) for x in self]
          return plist([call_attr(x, attrs[i], pepth=pepth - 1, call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA, *[a[i] for a in pargs], **{k: v[i] for k, v in pkwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

      # qj(self, 'Directly calling attr %r (%s) at pepth %d' % (attr, name, pepth), b=dbg * (not name.startswith('__')))
      if name in ['qj', 'me']:
        result = attr(call_pepth=call_pepth, *args, **kwargs)
      else:
        result = attr(*args, **kwargs)
      if result is None:
        return self
      return result

    if _pepth:
      wrap = lambda *a, **k: call_attr(self, attr, pepth=_pepth, *a, **k)
    else:
      wrap = lambda *a, **k: call_attr(self, attr, *a, **k)
    return wrap


  def __getitem__(self, key):
    try:
      if (isinstance(key, list)
          and plist(key).all(isinstance, int)):
        return qj(plist([self[k] for k in key]), 'return self[%s]' % str(key), b=0)  # Don't pass root -- we are uprooting
      elif isinstance(key, slice):
        if self is self.__root__:
          return plist(list.__getitem__(self, key))
        return plist(list.__getitem__(self, key), root=plist(list.__getitem__(self.__root__, key)))
      else:
        return qj(list.__getitem__(self, key), 'return list[%s]' % str(key), b=0)
    except TypeError as first_exception:
      try:
        if isinstance(key, list):
          return qj(plist([self[i][k] for i, k in enumerate(key)]), 'return self[i][%s]' % 'str(key)', b=0)  # Don't pass root -- we are uprooting
        if isinstance(key, tuple):
          try:
            return plist([x[key] for x in self], root=self.__root__)
          except Exception:
            return qj(plist([tuple(x[k] for k in key) for x in self], root=self.__root__), 'return self[%s]' % 'str(key)', b=0)
        return qj(plist([x[key] for x in self], root=self.__root__), 'return elements[%s]' % 'str(key)', b=0)
      except Exception as second_exception:
        raise TypeError('Failed to apply index to self or elements.\nself exception: %s\nelements exception: %s' % (str(first_exception), str(second_exception)))

  def __getslice__(self, i, j):
    return plist.__getitem__(self, slice(i, j))

  def __setattr__(self, name, value):
    if name == '__root__':
      list.__setattr__(self, name, value)
    elif not isinstance(value, STRING_TYPES) and hasattr(value, '__len__') and len(value) == len(self):
      for x, v in zip(self, value):
        x.__setattr__(name, v)
    else:
      for x in self:
        x.__setattr__(name, value)

  def __setitem__(self, key, value):
    list.__setitem__(self, key, value)
    return self

  def __setslice__(self, i, j, sequence):
    list.__setslice__(self, i, j, sequence)
    return self

  def __delattr__(self, name):
    for x in self:
      x.__delattr__(name)
    return self

  def __delitem__(self, key):
    list.__delitem__(self, key)
    return self

  def __delslice__(self, i, j):
    list.__delslice__(self, i, j)
    return self

  __hash__ = None


  def __call__(self, *args, **kwargs):
    pepth = kwargs.pop('pepth', 0)
    call_pepth = kwargs.pop('call_pepth', 0)
    args = [_ensure_len(len(self), a) for a in args]
    kwargs = {
        k: _ensure_len(len(self), v) for k, v in kwargs.items()
    }
    if pepth != 0:
      if not isinstance(self, plist):
        raise Exception  # ('Attempting to plist.__call__ object of type %s' % type(self))
      # qj(self, 'About to try calling at pepth %d' %  pepth, b=dbg)
      pargs = args
      pkwargs = kwargs
      if pepth < 0:
        try:
          return plist([x(pepth=pepth - 1, call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA, *[a[i] for a in pargs], **{k: v[i] for k, v in pkwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
        except Exception as e:
          pass
      else:
        return plist([x(pepth=pepth - 1, call_pepth=call_pepth + PLIST_CALL_ATTR_CALL_PEPTH_DELTA, *[a[i] for a in pargs], **{k: v[i] for k, v in pkwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

    # qj(self, 'Directly calling at pepth %d' %  pepth, b=dbg)
    return plist([x(*[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)


  def __contains__(self, other):
    return list.__contains__(self, other)


  __cmp__ = _build_comparator(
      operator.__eq__,
      operator.__or__,
      lambda self, return_inds: (
          self.lfill(-1, pepth=-1)
          if return_inds else self))
  __eq__ = __cmp__

  __ne__ = _build_comparator(
      operator.__ne__,
      operator.__and__,
      lambda self, return_inds: ([] if return_inds else plist()))

  __gt__ = _build_comparator(
      operator.__gt__,
      operator.__and__,
      lambda self, return_inds: ([] if return_inds else plist()))

  __ge__ = _build_comparator(
      operator.__ge__,
      operator.__and__,
      lambda self, return_inds: (
          self.lfill(-1, pepth=-1)
          if return_inds else self))

  __lt__ = _build_comparator(
      operator.__lt__,
      operator.__and__,
      lambda self, return_inds: ([] if return_inds else plist()))

  __le__ = _build_comparator(
      operator.__le__,
      operator.__and__,
      lambda self, return_inds: (
          self.lfill(-1, pepth=-1)
          if return_inds else self))


  __and__ = _build_logical_op(operator.__and__)
  __rand__ = _build_binary_rop(operator.__and__)
  __iand__ = _build_binary_op(operator.__iand__)

  __or__ = _build_logical_op(operator.__or__)
  __ror__ = _build_binary_rop(operator.__or__)
  __ior__ = _build_binary_op(operator.__ior__)

  __xor__ = _build_logical_op(operator.__xor__)
  __rxor__ = _build_binary_rop(operator.__xor__)
  __ixor__ = _build_binary_op(operator.__ixor__)


  __add__, __radd__, __iadd__ = _build_binary_ops(operator.__add__, operator.__iadd__)

  __sub__, __rsub__, __isub__ = _build_binary_ops(operator.__sub__, operator.__isub__)

  __mul__, __rmul__, __imul__ = _build_binary_ops(operator.__mul__, operator.__imul__)

  if sys.version_info[0] < 3:
    __div__, __rdiv__, __idiv__ = _build_binary_ops(operator.__div__, operator.__idiv__)

  __mod__, __rmod__, __imod__ = _build_binary_ops(operator.__mod__, operator.__imod__)

  __floordiv__, __rfloordiv__, __ifloordiv__ = _build_binary_ops(operator.__floordiv__, operator.__ifloordiv__)

  __divmod__ = _build_binary_op(divmod)
  __rdivmod__ = _build_binary_rop(divmod)

  __pow__, __rpow__, __ipow__ = _build_binary_ops(operator.__pow__, operator.__ipow__)

  __lshift__, __rlshift__, __ilshift__ = _build_binary_ops(operator.__lshift__, operator.__ilshift__)

  __rshift__, __rrshift__, __irshift__ = _build_binary_ops(operator.__rshift__, operator.__irshift__)

  __truediv__, __rtruediv__, __itruediv__ = _build_binary_ops(operator.__truediv__, operator.__itruediv__)


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


  # Nope.  Crashes when trying to index by plists of lists of ints.
#   def __index__(self):
#     qj(d=1)
#     return plist([x.__index__() for x in self], root=self.__root__)


  def __enter__(self):
    qj(d=1)
    return plist([x.__enter__() for x in self], root=self.__root__)

  def __exit__(self, exc_type, exc_value, traceback):
    qj(d=1)
    return plist([x.__exit__(exc_type, exc_value, traceback) for x in self], root=self.__root__)


  def root(self):
    return self.__root__

  def uproot(self):
    self.__root__ = self
    return self

#   def and(self, root=True):
#     # Interesting idea, but definitely doesn't work like this
#     return plist([x.__root__.append(x) if isinstance(x, plist) else plist([x], root=self) for x in self], root=self.__root__)

  def all(self, func, *args, **kwargs):
    for x in self:
      if not func(x, *args, **kwargs):
        return plist()
    return self

  def any(self, func, *args, **kwargs):
    for x in self:
      if func(x, *args, **kwargs):
        return self
    return plist()

  def none(self, func, *args, **kwargs):
    for x in self:
      if func(x, *args, **kwargs):
        return plist()
    return self

  def apply(self, func, *args, **kwargs):
    paslist = kwargs.pop('paslist', False)
    args = [_ensure_len(len(self), a) for a in args]
    kwargs = {
        k: _ensure_len(len(self), v) for k, v in kwargs.items()
    }
    if isinstance(func, str):
      func = plist.__getattribute__(self, func)
      if hasattr(func, '__len__') and len(func) == len(self):
        return plist([func[i](*[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
      else:
        # We should be calling a single function of a plist object.  If that's not the case, something odd is happening, and the crash is appropriate.
        return func(*[a[0] for a in args], **{k: v[0] for k, v in kwargs.items()})
    if paslist:
      return plist([plist(func(x.aslist(), *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}), root=x.__root__) for i, x in enumerate(self)], root=self.__root__)
    else:
      return plist([func(x, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

  def aslist(self):
    try:
      return [x.aslist() for x in self]
    except Exception as e:
      pass
    return [x for x in self]

  def astuple(self):
    try:
      return tuple([x.astuple() for x in self])
    except Exception as e:
      pass
    return tuple([x for x in self])

  def groupby(self):
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
    return plist([self])

  def me(self, name_or_plist='me', call_pepth=0):
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

  def nonempty(self, r=1):
    if r > 1 or r < 0:
      try:
        new_plist = plist([x.nonempty(r=r - 1) for x in self if len(x)])
      except Exception:
        new_plist = self
    else:
      new_plist = self
    return plist([x for x in new_plist if len(x)])

  def np(self, *args, **kwargs):
    return plist([np.array(x, *args, **kwargs) for x in self], root=self.__root__)

  def pd(self, *args, **kwargs):
    return pd.DataFrame.from_records(self.aslist(), *args, **kwargs)

  def pset(self):
    return plist([pset(x) for x in self], root=self.__root__)

  def pfill(self, v=0, s=None):
    s = pdict(v=v, s=lambda: s.update(v=s.v + 1).v) if s is None else s
    try:
      return plist([x.pfill(s=s) for i, x in enumerate(self)], root=self.__root__)
    except Exception:
      return plist([s.s() for _ in range(len(self))], root=self.__root__)

  def lfill(self, v=0, s=None):
    s = pdict(v=v, s=lambda: s.update(v=s.v + 1).v) if s is None else s
    try:
      return [x.lfill(s=s) for i, x in enumerate(self)]
    except Exception:
      return [s.s() for _ in range(len(self))]

  def pleft(self):
    return -self.pfill() + self.plen(-1).ungroup(-1)[0]

  def plen(self, r=1):
    if r > 1 or r < 0:
      try:
        return plist([sum(x.plen(r - 1) for x in self)], root=self.__root__)
      except Exception:
        pass
    return plist([len(self)], root=self.__root__)

  def rlen(self, r=1):
    if r > 1 or r < 0:
      try:
        return plist([x.plen(r - 1) for x in self], root=self.__root__)
      except Exception:
        pass
    return plist([len(self)], root=self.__root__)

  def pshape(self):
    try:
      return plist([x.pshape() for x in self], root=self.__root__)
    except Exception:
      return plist([len(self)], root=self.__root__)

  def preduce_eq(self):
    vals = pset()
    new_items = []
    new_roots = []
    not_root = (not self is self.__root__)
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

  def pstr(self):
    try:
      return plist([x.pstr() for x in self], root=self.__root__)
    except Exception:
      return plist([str(x) for x in self], root=self.__root__)

  def qj(self, *args, **kwargs):
    call_pepth = kwargs.pop('call_pepth', 0)
    return qj(self, _depth=4 + call_pepth, *args, **kwargs)

  def remix(self, *args, **kwargs):
    kwargs = {
        k: _ensure_len(len(self), v) for k, v in kwargs.items()
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

  def sortby(self, key=None, reverse=False):
    key = key or (lambda x: x)
    sorted_inds = [i for i, _ in sorted(enumerate(self), key=lambda x: key(x[1]), reverse=reverse)]
    self.__root__[:] = self.__root__[sorted_inds]
    if self is not self.__root__:
      self[:] = self[sorted_inds]
    return self

  def ungroup(self, r=1):
    new_items = []
    for g in self:
      if not isinstance(g, list):
        if r < 0:
          return self
        raise ValueError('Called ungroup on a plist that has non-group children')
      for x in g:
        new_items.append(x)
    if r > 1 or r < 0 and len(new_items):
      return plist(new_items).ungroup(r - 1)
    return plist(new_items)

#   def ungroup(self, r=1):
#     if r != 0:
#       try:
#         return plist([x.ungroup(r - 1) for x in self.__root__])
#       except Exception:
#         pass

#     new_items = []
#     for g in self.__root__:
#       if not isinstance(g, list):
#         if r < 0:
#           return self
#         raise ValueError('Called ungroup on a plist that has non-group children')
#       for x in g:
#         new_items.append(x)
#     if r > 1 or r < 0:
#       return plist(new_items).ungroup(r - 1)
#     return plist(new_items)

  def values_like(self, value=0):
    values = _ensure_len(len(self), value)
    try:
      return plist([x.values_like(v) for x, v in zip(self, values)], root=self.__root__)
    except Exception:
      pass
    return plist([v for v in values], root=self.__root__)


pist = plist


def _ensure_len(length, x):
  if not isinstance(x, type) and not isinstance(x, str) and not isinstance(x, tuple) and hasattr(x, '__len__') and len(x) == length:
    return x
  return [x for _ in range(length)]


def _merge_indices(left, right, op):
  # qj((left, right), 'l,r', b=0)
  try:
    left_empty_or_ints = len(left) == 0 or plist(left).all(isinstance, int)
    right_empty_or_ints = len(right) == 0 or plist(right).all(isinstance, int)
    if left_empty_or_ints and right_empty_or_ints:
      sl = set(left)
      sr = set(right)
      return qj(sorted(list(op(sl, sr))), 'ret left op right', b=0)
  except Exception:
    pass
  try:
    return qj([_merge_indices(left[i], right[i], op) for i in range(max(len(left), len(right)))], 'ret merge(l[i], r[i])', b=0)
  except Exception:
    pass
  if isinstance(left, list) and isinstance(right, list):
    return qj(left.extend(right) or left, 'ret left.extend(right)', b=0)
  return qj([left, right], 'ret [l, r]', b=1, d=1)


