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
from collections import namedtuple

import functools
from functools import partial
import operator
import os
import types

import numpy as np
import pandas as pd
from qj_global import qj


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
    if isinstance(key, list) and not isinstance(value, types.StringTypes) and hasattr(value, '__len__') and len(value) == len(key):
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
#       raise AttributeError('\'%s\' object has no attribute \'%s\'' % (type(self), name))
    if name == '*':
      return plist([self[k] for k in self])
    return self[name]

  def __setattr__(self, name, value):
    self[name] = value

  def __cmp__(self, other):
    return self is other

  __eq__ = __cmp__

  def __ne__(self, other):
    return not self == other

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
    if isinstance(key, list) and not isinstance(value, types.StringTypes) and hasattr(value, '__len__') and len(value) == len(key):
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
class plist(list):  # pylint: disable=invalid-name
  """List where everything is automatically a property that is applied to its elements.  Guaranteed to surprise, if not delight."""

  def __init__(self, *args, **kwargs):
    depth = qj(kwargs.pop('depth', 1), b=0)
    self.__root__ = qj(kwargs.pop('root', self), b=0)
    if depth == 1:
      list.__init__(self, *args, **kwargs)
    else:
      # Don't pass root through when making nested plists, because that doesn't make any sense.
      plist.__init__(self, [plist(*args, depth=depth - 1, **kwargs)])

  def __getattribute__(self, name):
    if name == '__root__':
      return list.__getattribute__(self, name)
    if name.startswith('___'):
      # Let people call reserved members of elements by using, e.g., ___len__().
      name = name[1:]
    elif name.startswith('__') and name.endswith('__'):
      raise qj(AttributeError('\'%s\'  objects cannot call reserved members of their elements: \'%s\'' % (type(self), name)), l=lambda _: self, b=0*dbg)
    qj(self, name, b=dbg)
    try:
      return qj(self.__getattr__(name), name, b=dbg)
    except AttributeError:
      qj(self, 'caught AttributeError for %s' % name, b=dbg)
      pass
    if not name.startswith('__') and name.endswith('_'):
      # Allows calling one level deeper by adding '_' to the end of a property name.  This is recursive, so '__' on the end goes two levels deep, etc.
      name = name[:-1]
    try:
      qj(name, 'trying', b=0)
      return qj(plist([(qj(hasattr(*qj((x, name), 'calling hasattr', l=lambda y: (self, y[0], type(y[0])), b=dbg)), 'hasattr %s' % name, l=lambda _: (self, x, type(x)), b=dbg)
                       and getattr(x, name))
                      or x[name] for x in self], root=self.__root__), name, b=dbg)
    except Exception as e:
      raise qj(AttributeError('\'%s\' object has no attribute \'%s\' (%s)' % (type(self), name, str(e))), l=lambda _: self, b=dbg)

  def __getattr__(self, name):
    qj(self, name, b=dbg * (not name.startswith('__')))
    attr = None
    if attr is None:
      attr = list.__getattribute__(self, name)
    def not_none_or_self(x):
      if x is None:
        return self
      return x
    return qj(lambda *a, **k: not_none_or_self(attr(*a, **k)), name, l=lambda _: self, b=dbg * (not name.startswith('__')))

  def __getitem__(self, key):
    try:
      if (isinstance(key, list)
          and plist(key).all(isinstance, int)):
        return qj(plist([self[k] for k in key]), 'return self[%s]' % str(key), b=0)  # Don't pass root -- we are uprooting
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
    if self is self.__root__:
      return plist(list.__getslice__(self, i, j))
    return plist(list.__getslice__(self, i, j), root=plist(list.__getslice__(self.__root__, i, j)))

  def __setattr__(self, name, value):
    if name == '__root__':
      list.__setattr__(self, name, value)
    elif not isinstance(value, types.StringTypes) and hasattr(value, '__len__') and len(value) == len(self):
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
    return qj(plist([x(*args, **kwargs) for x in self], root=self.__root__), '__call__', b=dbg)

  def __contains__(self, other):
    return list.__contains__(self, other)


  def __and__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        try:
          return plist([x & o for x, o in zip(self, other)])
        except Exception:
          pass
      self_flat = self.ungroup(-1)
      ids = set([id(x) for x in self_flat]) & set([id(x) for x in other.ungroup(-1)])
      return plist([x for x in self_flat if id(x) in ids])  # Don't pass root -- we are uprooting
    else:
      return plist([(x & other) for x in self], root=self.__root__)

  def __or__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        try:
          return plist([x | o for x, o in zip(self, other)])
        except Exception:
          pass
      self_flat = self.ungroup(-1)
      other_flat = other.ungroup(-1)
      ids = set([id(x) for x in self_flat]) | set([id(x) for x in other_flat])
      return plist(
          [ids.remove(id(x)) or x for x in self_flat if id(x) in ids] +
          [ids.remove(id(x)) or x for x in other_flat if id(x) in ids]
      )  # Don't pass root -- we are uprooting
    else:
      return plist([(x | other) for x in self], root=self.__root__)

  def __xor__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        try:
          return plist([x ^ o for x, o in zip(self, other)])
        except Exception:
          pass
      self_flat = self.ungroup(-1)
      other_flat = other.ungroup(-1)
      ids = set([id(x) for x in self_flat]) ^ set([id(x) for x in other_flat])
      return plist(
          [ids.remove(id(x)) or x for x in self_flat if id(x) in ids] +
          [ids.remove(id(x)) or x for x in other_flat if id(x) in ids]
      )  # Don't pass root -- we are uprooting
    else:
      return plist([(x ^ other) for x in self], root=self.__root__)


  def __add__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x + o for x, o in zip(self, other)], root=self.__root__)
    return plist([x + other for x in self], root=self.__root__)

  def __radd__(self, other):
    return plist([other + x for x in self], root=self.__root__)

  def __iadd__(self, other):
    if isinstance(other, plist):
      return plist(list.__iadd__(self, other))
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x += other
    return new_plist


  def __sub__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x - o for x, o in zip(self, other)], root=self.__root__)
    return plist([x - other for x in self], root=self.__root__)

  def __rsub__(self, other):
    return plist([other - x for x in self], root=self.__root__)

  def __isub__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x -= other
    return new_plist


  def __mul__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x * o for x, o in zip(self, other)], root=self.__root__)
    return plist([x * other for x in self], root=self.__root__)

  def __rmul__(self, other):
    return plist([other * x for x in self], root=self.__root__)

  def __imul__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x *= other
    return new_plist


  def __div__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x / o for x, o in zip(self, other)], root=self.__root__)
    return plist([x / other for x in self], root=self.__root__)

  def __rdiv__(self, other):
    return plist([other / x for x in self], root=self.__root__)

  def __idiv__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x /= other
    return new_plist


  def __mod__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x % o for x, o in zip(self, other)], root=self.__root__)
    return plist([x % other for x in self], root=self.__root__)

  def __rmod__(self, other):
    return plist([other % x for x in self], root=self.__root__)

  def __imod__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x %= other
    return new_plist


  def __floordiv__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x // o for x, o in zip(self, other)], root=self.__root__)
    return plist([x // other for x in self], root=self.__root__)

  def __divmod__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([divmod(x, o) for x, o in zip(self, other)], root=self.__root__)
    return plist([divmod(x, other) for x in self], root=self.__root__)

  def __pow__(self, *args):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([pow(x, *args) for x, o in zip(self, other)], root=self.__root__)
    return plist([pow(x, *args) for x in self], root=self.__root__)

  def __lshift__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x << o for x, o in zip(self, other)], root=self.__root__)
    return plist([x << other for x in self], root=self.__root__)

  def __rshift__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x >> o for x, o in zip(self, other)], root=self.__root__)
    return plist([x >> other for x in self], root=self.__root__)

  def __truediv__(self, other):
    if isinstance(other, plist):
      if len(self) == len(other):
        return plist([x / o for x, o in zip(self, other)], root=self.__root__)
    return plist([x / other for x in self], root=self.__root__)


  def __rtruediv__(self, other):
    return plist([other / x for x in self], root=self.__root__)

  def __rfloordiv__(self, other):
    return plist([other // x for x in self], root=self.__root__)

  def __rdivmod__(self, other):
    return plist([divmod(other, x) for x in self], root=self.__root__)

  def __rpow__(self, other):
    return plist([other ** x for x in self], root=self.__root__)

  def __rlshift__(self, other):
    return plist([other << x for x in self], root=self.__root__)

  def __rrshift__(self, other):
    return plist([other >> x for x in self], root=self.__root__)

  def __rand__(self, other):
    return plist([other & x for x in self], root=self.__root__)

  def __rxor__(self, other):
    return plist([other ^ x for x in self], root=self.__root__)

  def __ror__(self, other):
    return plist([other | x for x in self], root=self.__root__)


  def __itruediv__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x /= other
    return new_plist

  def __ifloordiv__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x //= other
    return new_plist

  def __imod__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x %= other
    return new_plist

  def __ipow__(self, *args):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x = pow(x, *args)
    return new_plist

  def __ilshift__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x <<= other
    return new_plist

  def __irshift__(self, other):
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x >>= other
    return new_plist

  def __iand__(self, other):
    qj(d=1)
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x &= other
    return new_plist

  def __ixor__(self, other):
    qj(d=1)
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x ^= other
    return new_plist

  def __ior__(self, other):
    qj(d=1)
    new_plist = plist(self, root=self.__root__)
    for x in new_plist:
      x |= other
    return new_plist


  def __neg__(self):
    return plist([-x for x in self], root=self.__root__)

  def __pos__(self):
    return plist([+x for x in self], root=self.__root__)

  def __abs__(self):
    return plist([abs(x) for x in self], root=self.__root__)

  def __invert__(self):
    return plist([~x for x in self], root=self.__root__)

  def __complex__(self):
    return plist([complex(x) for x in self], root=self.__root__)

  def __int__(self):
    return plist([int(x) for x in self], root=self.__root__)

  def __long__(self):
    return plist([long(x) for x in self], root=self.__root__)

  def __float__(self):
    return plist([float(x) for x in self], root=self.__root__)

  def __oct__(self):
    return plist([oct(x) for x in self], root=self.__root__)

  def __hex__(self):
    return plist([hex(x) for x in self], root=self.__root__)


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

  def aslist(self):
    try:
      return [x.aslist() for x in self]
    except Exception as e:
      pass
    return [x for x in self]

  def apply(self, func, *args, **kwargs):
    pepth = kwargs.pop('pepth', 0)
    args = [_ensure_len(len(self), a) for a in args]
    kwargs = {
        k: _ensure_len(len(self), v) for k, v in kwargs.items()
    }
    qj((self, func, args, kwargs), 'apply called', b=0)
    if pepth != 0:
      if pepth < 0:
        try:
          return plist([x.apply(func, pepth=pepth - 1, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
        except Exception as e:
          # qj((self, func, e), 'caught exception applying function, ignoring.', b=0)
          pass
      else:
        return plist([x.apply(func, pepth=pepth - 1, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
    if isinstance(func, str):
      func = self.__getattribute__(func)
      if hasattr(func, '__len__') and len(func) == len(self):
        return plist([func[i](*[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)
      else:
        # We should be calling a single function of a plist object.  If that's not the case, something odd is happening, and the crash is appropriate.
        return func(*[a[0] for a in args], **{k: v[0] for k, v in kwargs.items()})
    return plist([func(x, *[a[i] for a in args], **{k: v[i] for k, v in kwargs.items()}) for i, x in enumerate(self)], root=self.__root__)

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

  def pstr(self):
    try:
      return plist([x.pstr() for x in self], root=self.__root__)
    except Exception:
      return plist([str(x) for x in self], root=self.__root__)

  def qj(self, *args, **kwargs):
    return qj(self, _depth=3, *args, **kwargs)

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


  def __cmp__(self, other, return_inds=False):
    if self is other:
      if return_inds:
        return qj(self.apply('lfill', -1, pepth=-1), 'lfill(-1)', b=0)
      else:
        return self
    qj((self, other), '(self, other)', b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = x.__cmp__(o, return_inds=True)
          inds.append(child_inds)
        elif x == o:
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = self.__cmp__(other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, self.__cmp__(o, return_inds=True), operator.__or__)
      qj((inds, self, other), 'inds self.cmp(other)', b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = x.__cmp__(other, return_inds=True)
          inds.append(child_inds)
        elif x == other:
          inds.append(i)

    qj(inds, 'inds cmp self: %s other: %s' % ('str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds cmp self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return cmp self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

  __eq__ = __cmp__

  def __ne__(self, other, return_inds=False):
    if self is other:
      if return_inds:
        return []
      return plist()
    qj((self, other), b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = x.__ne__(o, return_inds=True)
          inds.append(child_inds)
        elif x != o:
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = self.__ne__(other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, self.__ne__(o, return_inds=True), operator.__and__)
      qj((inds, self, other), 'inds self.ne(other)', b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = x.__ne__(other, return_inds=True)
          inds.append(child_inds)
        elif x != other:
          inds.append(i)

    qj(inds, 'inds ne self: %s other: %s' % ('str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds ne self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return ne self: %s other: %s' % ('str(self)', 'str(other)'), b=0)


  def __gt__(self, other, return_inds=False):
    if self is other:
      return plist()
    qj((self, other), b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = x.__gt__(o, return_inds=True)
          inds.append(child_inds)
        elif x > o:
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = self.__gt__(other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, self.__gt__(o, return_inds=True), operator.__and__)
      qj((inds, self, other), 'inds self.gt(other)', b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = x.__gt__(other, return_inds=True)
          inds.append(child_inds)
        elif x > other:
          inds.append(i)

    qj(inds, 'inds gt self: %s other: %s' % ('str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds gt self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return gt self: %s other: %s' % ('str(self)', 'str(other)'), b=0)


  def __ge__(self, other, return_inds=False):
    if self is other:
      if return_inds:
        return qj(self.apply('lfill', -1, pepth=-1), 'lfill(-1)', b=0)
      else:
        return self
    qj((self, other), b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = x.__ge__(o, return_inds=True)
          inds.append(child_inds)
        elif x >= o:
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = self.__ge__(other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, self.__ge__(o, return_inds=True), operator.__and__)
      qj((inds, self, other), 'inds self.ge(other)', b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = x.__ge__(other, return_inds=True)
          inds.append(child_inds)
        elif x >= other:
          inds.append(i)

    qj(inds, 'inds ge self: %s other: %s' % ('str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds ge self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return ge self: %s other: %s' % ('str(self)', 'str(other)'), b=0)


  def __lt__(self, other, return_inds=False):
    if self is other:
      return plist()
    qj((self, other), b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = x.__lt__(o, return_inds=True)
          inds.append(child_inds)
        elif x < o:
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = self.__lt__(other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, self.__lt__(o, return_inds=True), operator.__and__)
      qj((inds, self, other), 'inds self.lt(other)', b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = x.__lt__(other, return_inds=True)
          inds.append(child_inds)
        elif x < other:
          inds.append(i)

    qj(inds, 'inds lt self: %s other: %s' % ('str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds lt self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return lt self: %s other: %s' % ('str(self)', 'str(other)'), b=0)


  def __le__(self, other, return_inds=False):
    if self is other:
      if return_inds:
        return qj(self.apply('lfill', -1, pepth=-1), 'lfill(-1)', b=0)
      else:
        return self
    qj((self, other), b=0)
    inds = []
    if isinstance(other, list) and len(self) == len(other):
      for i, (x, o) in enumerate(zip(self, other)):
        if isinstance(x, plist):
          child_inds = x.__le__(o, return_inds=True)
          inds.append(child_inds)
        elif x <= o:
          inds.append(i)
    elif isinstance(other, list) and len(other) > 0:
      inds = self.__le__(other[0], return_inds=True)
      for o in other[1:]:
        inds = _merge_indices(inds, self.__le__(o, return_inds=True), operator.__and__)
      qj((inds, self, other), 'inds self.le(other)', b=0)
    else:
      for i, x in enumerate(self):
        if isinstance(x, plist):
          child_inds = x.__le__(other, return_inds=True)
          inds.append(child_inds)
        elif x <= other:
          inds.append(i)

    qj(inds, 'inds le self: %s other: %s' % ('str(self)', 'str(other)'), b=0)
    if return_inds:
      return qj(inds, 'return inds le self: %s other: %s' % ('str(self)', 'str(other)'), b=0)

    return qj(self.__root__[inds], 'return le self: %s other: %s' % ('str(self)', 'str(other)'), b=0)


pist = plist


def _ensure_len(length, x):
  if not isinstance(x, str) and not isinstance(x, tuple) and hasattr(x, '__len__') and len(x) == length:
    return x
  return [x for _ in range(length)]


def _merge_indices(left, right, op):
  qj((left, right), 'l,r', b=0)
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


