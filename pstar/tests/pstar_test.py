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

# pylint: disable=line-too-long
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict
import os
import re
import shutil
import sys
import tempfile

import unittest
import mock

import matplotlib.pyplot as plt
import numpy as np

from pstar import defaultpdict, frozenpset, pdict, plist, pset, ptuple, pstar  # pylint: disable=g-multiple-import
from qj import qj

DEBUG_TESTS = False


class RegExp(object):

  def __init__(self, pattern, flags=0):
    self._p = pattern
    self._f = flags

  def __eq__(self, o):
    if DEBUG_TESTS:
      print('%s: %s: \'%s\'' % ('pass' if bool(re.search(self._p, o, self._f)) else 'FAIL', str(self), str(o)))
    return bool(re.search(self._p, o, self._f))

  def __ne__(self, o):
    return not self.__eq__(o)

  def __repr__(self):
    return '<RegExp:(%s)>' % self._p


class PStarTest(unittest.TestCase):

  def setUp(self):
    pass

  def test_empty_pdict(self):
    self.assertFalse(pdict())

  def test_pdict_assignment(self):
    p = pdict()
    p.foo = 1
    self.assertEqual(p['foo'], 1)

    p = pdict(foo=1, bar=2)
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [1, 2])

    p = pdict()
    p[['foo', 'bar']] = 1
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [1, 1])

    p[['foo', 'bar']] = [1, 2]
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [1, 2])

  def test_pdict_update(self):
    p = pdict(foo=1, bar=2)
    p.update(bar=3).baz = 4
    self.assertEqual(p.bar, 3)
    self.assertIn('baz', p.keys())

  def test_pdict_peys(self):
    p = pdict(foo=1, bar=2, floo=0)

    self.assertEqual(p.peys().aslist(),
                     sorted(p.keys()))

    # Filter p by keys and then by values
    self.assertEqual((p[p.peys()._[0] == 'f'] > 0).aslist(),
                     [('foo', 1)])

    self.assertEqual((p[p.peys()._[0] == 'f'] > 0).pdict(),
                     dict(foo=1))

    # Create a new pdict mapping keys to the first letter of the keys.
    # Really is testing plist.pdict()...
    self.assertEqual(p.peys()._[0].pdict(),
                     pdict(foo='f', bar='b', floo='f'))

    # Supress warning message on python 2.7.
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False
      p[p.peys()._[1:]] = p[p.peys()] * 3
    qj.LOG_FN = log_fn
    qj.COLOR = True
    self.assertEqual(p,
                     dict(foo=1, bar=2, floo=0, oo=3, ar=6, loo=0))

  def test_pdict_palues(self):
    p = pdict(foo=1, bar=2, floo=0)

    self.assertEqual(p.palues().aslist(),
                     [2, 0, 1])

    self.assertEqual((p.palues() == 0).aslist(),
                     [('floo', 0)])

    self.assertEqual((p.palues() > 0).pdict(),
                     dict(foo=1, bar=2))

    self.assertEqual((p.palues() + 1).pdict(),
                     dict(foo=2, bar=3, floo=1))

  def test_pdict_pitems(self):
    p = pdict(foo=1, bar=2, floo=0)

    self.assertEqual(p.pitems().aslist(),
                     [('bar', 2), ('floo', 0), ('foo', 1)])

    self.assertEqual((p.pitems() > ('bar', 2)).aslist(),
                     [('floo', 0), ('foo', 1)])

  def test_pdict_rekey(self):
    p = pdict(foo=1, bar=2, floo=0)

    self.assertEqual(p.rekey({'floo': 'baz'}),
                     dict(foo=1, bar=2, baz=0))

    self.assertEqual(p.rekey(lambda k: 'bin' if k == 'floo' else k),
                     dict(foo=1, bar=2, bin=0))

    self.assertEqual(p.rekey(floo='blaz'),
                     dict(foo=1, bar=2, blaz=0))

    self.assertRaises(ValueError, lambda: p.rekey(13))
    self.assertRaises(ValueError, lambda: p.rekey({'floo': 'foo'}))

    pp = p.copy()
    pp.rekey({'floo': 'bin'}, inplace=True)
    self.assertEqual(p,
                     dict(foo=1, bar=2, floo=0))
    self.assertEqual(pp,
                     dict(foo=1, bar=2, bin=0))

    pp = p.copy()
    pp.rekey({'foo': 'floo'}, floo='bin', inplace=True)
    self.assertEqual(p,
                     dict(foo=1, bar=2, floo=0))
    self.assertEqual(pp,
                     dict(floo=1, bar=2, bin=0))

  def test_empty_defaultpdict(self):
    self.assertFalse(defaultpdict())

  def test_defaultpdict_int_default(self):
    p = defaultpdict(int)
    self.assertEqual(p.foo, 0)

  def test_defaultpdict_copy(self):
    p = defaultpdict(int)
    p.foo = 0
    pp = p.copy()
    self.assertEqual(p, pp)
    self.assertEqual(p.foo, pp.foo)
    p.foo = 1
    self.assertNotEqual(p.foo, pp.foo)
    self.assertIsInstance(pp, defaultpdict)

  def test_defaultpdict_nested_constructor(self):
    p = defaultpdict(lambda: defaultpdict(list))
    p.foo = 1
    p.stats.bar.append(2)
    self.assertEqual(p['foo'], 1)
    self.assertEqual(p.stats.bar, [2])

  def test_defaultpdict_assignment(self):
    p = defaultpdict(int)
    p.foo = 1
    self.assertEqual(p['foo'], 1)

    p = defaultpdict(foo=1, bar=2)
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [1, 2])

    p = defaultpdict(int)
    p[['foo', 'bar']] = 1
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [1, 1])

    p[['foo', 'bar']] = [1, 2]
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [1, 2])

    p = defaultpdict(list)
    p[['foo', 'bar']].append_(1)
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [[1], [1]])

    p[['foo', 'bar']].append_(plist[2, 3])
    self.assertEqual(p[['foo', 'bar']].aslist(),
                     [[1, 2], [1, 3]])

    p[['baz', 'bin']].append_(plist[0, 1])
    self.assertEqual(p[['baz', 'bin']].aslist(),
                     [[0], [1]])

  def test_defaultpdict_update(self):
    p = pdict(foo=1, bar=2)
    p.update(bar=3).baz = 4
    self.assertEqual(p.bar, 3)
    self.assertIn('baz', p.keys())

  def test_defaultpdict_rekey(self):
    p = defaultpdict(int).update(foo=1, bar=2, floo=0)

    self.assertEqual(p.rekey({'floo': 'baz'}),
                     dict(foo=1, bar=2, baz=0))

    self.assertEqual(p.rekey(lambda k: 'bin' if k == 'floo' else k),
                     dict(foo=1, bar=2, bin=0))

    self.assertEqual(p.rekey(floo='blaz'),
                     dict(foo=1, bar=2, blaz=0))

    self.assertRaises(ValueError, lambda: p.rekey(13))
    self.assertRaises(ValueError, lambda: p.rekey({'floo': 'foo'}))

    pp = p.copy()
    pp.rekey({'floo': 'bin'}, inplace=True)
    self.assertEqual(p,
                     dict(foo=1, bar=2, floo=0))
    self.assertEqual(pp,
                     dict(foo=1, bar=2, bin=0))

    pp = p.copy()
    pp.rekey({'foo': 'floo'}, floo='bin', inplace=True)
    self.assertEqual(p,
                     dict(foo=1, bar=2, floo=0))
    self.assertEqual(pp,
                     dict(floo=1, bar=2, bin=0))

  def test_empty_plist(self):
    self.assertFalse(plist())

  def test_empty_plist_ungroup(self):
    self.assertFalse(plist().ungroup(-1))

  def test_plist_init(self):
    pl = plist([x for x in range(4)])
    self.assertEqual(pl.aslist(),
                     [0, 1, 2, 3])

  def test_plist_convenience_init_from_array(self):
    pl = plist[0, 1, 2, 3]
    self.assertEqual(pl.aslist(),
                     [0, 1, 2, 3])

  def test_plist_of_int_to_float(self):
    pl = plist([1, 2, 3])

    self.assertEqual(pl.apply(float).pstr().aslist(),
                     ['1.0', '2.0', '3.0'])

  def test_plist_apply_with_list_of_fn(self):
    pl = plist[1, 2, 3]
    fns = plist[lambda x: x + 1, lambda x: x + 2, lambda x: x + 3]

    self.assertEqual(pl.apply(fns).aslist(),
                     [2, 4, 6])

  def test_plist_apply_on_empty_plist(self):
    pl = plist()

    sentinal = lambda x: None

    self.assertEqual(pl.apply(sentinal).aslist(),
                     [])

  def test_plist_filter(self):
    pl = plist[1, 2, 3]
    fn = lambda x: x <= 2

    self.assertEqual(pl.filter(fn).aslist(),
                     [1, 2])

    pl2 = plist[1, 'b', None]
    self.assertEqual(pl2.filter().aslist(),
                     [1, 'b'])
    self.assertEqual(pl2.filter(isinstance, str).aslist(),
                     ['b'])

    plists = pdict(locals()).palues().filter(isinstance, plist).pdict()
    self.assertEqual(plists.peys().aslist(),
                     ['pl', 'pl2'])

  def test_plist_filter_with_list_of_fn(self):
    pl = plist[1, 2, 3]
    fns = plist[lambda x: x < 2, lambda x: x > 2, lambda x: x == 3]

    self.assertEqual(pl.filter(fns).aslist(),
                     [1, 3])

  def test_plist_negative_slicing(self):
    pl = plist()
    for i in range(10):
      pl.append(i)
      self.assertEqual(len(pl[-10:]),
                       min(10, len(pl)))

  def test_plist_of_list_easy_indexing(self):
    pl = plist([[i * 1, i * 2, i * 3] for i in range(3)])
    self.assertEqual(pl.aslist(),
                     [[0, 0, 0],
                      [1, 2, 3],
                      [2, 4, 6]])
    self.assertEqual(pl[0],
                     [0, 0, 0])
    self.assertEqual(pl._[0].aslist(),
                     [0, 1, 2])

  def test_plist_of_list_easy_slicing(self):
    pl = plist([[i * 1, i * 2, i * 3] for i in range(3)])
    self.assertEqual(pl.aslist(),
                     [[0, 0, 0],
                      [1, 2, 3],
                      [2, 4, 6]])
    self.assertEqual(pl[1:],
                     [[1, 2, 3],
                      [2, 4, 6]])
    if sys.version_info[0] < 3:
      self.assertEqual(pl._[1::1].aslist(),
                       [[0, 0],
                        [2, 3],
                        [4, 6]])
      if '__warned__' in plist.__getslice__.__dict__:
        del plist.__getslice__.__dict__['__warned__']
      log_fn = qj.LOG_FN
      with mock.patch('logging.info') as mock_log_fn:
        qj.LOG_FN = mock_log_fn
        qj.COLOR = False
        pl._[1:]
        mock_log_fn.assert_called_once_with(RegExp('qj: <pstar> __getslice__: WARNING!'))

      qj.LOG_FN = log_fn
      qj.COLOR = True
    else:
      self.assertEqual(pl._[1:].aslist(),
                       [[0, 0],
                        [2, 3],
                        [4, 6]])

  def test_plist_all_any_none(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

    self.assertEqual(foos.bar.all().aslist(),
                     [])

    self.assertEqual(foos.bar.any().aslist(),
                     foos.bar.aslist())

    self.assertEqual(foos.bar.none().aslist(),
                     [])

    self.assertEqual(foos.all(isinstance, pdict).aslist(),
                     foos.aslist())

    self.assertEqual(foos.any(isinstance, pdict).aslist(),
                     foos.aslist())

    self.assertEqual(foos.none(isinstance, pdict).aslist(),
                     [])

  def test_plist_with_obj_method_with_trailing_underscore(self):
    class O(object):
      def foo_(self):
        return 1

    pl = plist([O() for _ in range(3)])

    self.assertEqual(pl.foo_().aslist(),
                     [1, 1, 1])

  def test_plist_comparators(self):
    foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertEqual(foo.aslist(),
                     [{'foo': 0, 'bar': 0},
                      {'foo': 1, 'bar': 1},
                      {'foo': 2, 'bar': 0}])
    zero_bars = foo.bar == 0
    self.assertEqual(zero_bars.aslist(),
                     [{'foo': 0, 'bar': 0},
                      {'foo': 2, 'bar': 0}])
    nonzero_bars = foo.bar != 0
    self.assertEqual(nonzero_bars.aslist(),
                     [{'foo': 1, 'bar': 1}])

    foo_eq_zero_bars = foo == zero_bars
    self.assertEqual(foo_eq_zero_bars.aslist(),
                     [{'foo': 0, 'bar': 0},
                      {'foo': 2, 'bar': 0}])
    foo_gt_bar = foo.foo > foo.bar
    self.assertEqual(foo_gt_bar.aslist(),
                     [{'foo': 2, 'bar': 0}])

    foo_eq_list = foo.foo == [0, 1, 3]
    self.assertEqual(foo_eq_list.aslist(),
                     [{'foo': 0, 'bar': 0},
                      {'foo': 1, 'bar': 1}])

    foo_by_bar_foo = foo.bar.groupby().foo.groupby()
    self.assertEqual(foo_by_bar_foo.aslist(),
                     [[[{'foo': 0, 'bar': 0}],
                       [{'foo': 2, 'bar': 0}]],
                      [[{'foo': 1, 'bar': 1}]]])
    nonzero_foo_by_bar_foo = foo_by_bar_foo.bar > 0
    self.assertEqual(nonzero_foo_by_bar_foo.aslist(),
                     [[[],
                       []],
                      [[{'bar': 1, 'foo': 1}]]])
    zero_foo_by_bar_foo = foo_by_bar_foo.foo != nonzero_foo_by_bar_foo.foo
    self.assertEqual(zero_foo_by_bar_foo.aslist(),
                     [[[{'foo': 0, 'bar': 0}],
                       [{'foo': 2, 'bar': 0}]],
                      [[]]])
    foo_by_bar_foo_eq_list = foo_by_bar_foo.foo == [[[0], [3]], [[1]]]
    self.assertEqual(foo_by_bar_foo_eq_list.aslist(),
                     [[[{'foo': 0, 'bar': 0}],
                       []],
                      [[{'foo': 1, 'bar': 1}]]])

    foo_eq_list = foo.foo == [0, 1, 3, 4]
    self.assertEqual(foo_eq_list.aslist(),
                     [{'foo': 0, 'bar': 0},
                      {'foo': 1, 'bar': 1}])
    foo_by_bar_foo_eq_list = foo_by_bar_foo.foo == [0, 1, 3, 4]
    self.assertEqual(foo_by_bar_foo_eq_list.aslist(),
                     [[[{'foo': 0, 'bar': 0}],
                       []],
                      [[{'foo': 1, 'bar': 1}]]])

    foo_eq_empty = foo.foo == []
    self.assertEqual(foo_eq_empty.aslist(),
                     [])
    foo_lt_empty = foo.foo < []
    self.assertEqual(foo_lt_empty.aslist(),
                     [{'foo': 0, 'bar': 0},
                      {'foo': 1, 'bar': 1},
                      {'foo': 2, 'bar': 0}])
    foo_by_bar_foo_eq_nonzero = foo_by_bar_foo == nonzero_foo_by_bar_foo
    self.assertEqual(foo_by_bar_foo_eq_nonzero.aslist(),
                     [[[],
                       []],
                      [[{'foo': 1, 'bar': 1}]]])
    foo_by_bar_foo_gt_nonzero = foo_by_bar_foo.foo > nonzero_foo_by_bar_foo.foo
    self.assertEqual(foo_by_bar_foo_gt_nonzero.aslist(),
                     [[[{'foo': 0, 'bar': 0}],
                       [{'foo': 2, 'bar': 0}]],
                      [[]]])

  def test_plist_of_filename_context_manager(self):
    path = os.path.dirname(__file__)
    filenames = plist(['__init__.py', 'pstar_test.py']).apply(lambda f: os.path.join(path, f))
    with filenames.apply(open, 'r') as f:
      texts = f.read()
    self.assertEqual(len(texts), 2)
    self.assertTrue(texts.all(isinstance, str))

  def test_plist_of_defaultpdict(self):
    foos = plist([defaultpdict(lambda: defaultpdict(plist)) for _ in range(3)])

    foos.foo.bar.append_(3)
    self.assertEqual(foos.foo.bar.aslist(),
                     [[3], [3], [3]])

    foos.append(4)
    self.assertEqual(foos[-1], 4)

  def test_plist_of_pdict_filter_and_update(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])

    self.assertEqual(foos.foo.aslist(),
                     [0, 1, 2])
    self.assertEqual(foos.bar.aslist(),
                     [0, 1, 0])

    (foos.bar == 0).update(dict(baz=3))

    self.assertEqual((foos.bar == 0).baz.aslist(),
                     [3, 3])
    self.assertRaises(AttributeError, lambda: (foos.bar != 0).baz)

  def test_plist_of_pdict_filter_and_assign(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3

    self.assertEqual((foos.bar == 0).baz.aslist(),
                     [3, 3])
    self.assertRaises(AttributeError, lambda: (foos.bar != 0).baz)

  def test_plist_of_pdict_filter_and_read(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.baz.aslist(), [3, 6, 5])

  def test_plist_of_pdict_slow_n2_grouping(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    # DON'T DO THIS! O^2!
    foos_by_bar = (plist([(foos.bar == bar) for bar in set(foos.bar)]))

    self.assertEqual(foos_by_bar.aslist(),
                     [[{'baz': 3, 'foo': 0, 'bar': 0},
                       {'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'baz': 6, 'foo': 1, 'bar': 1}]])

  def test_plist_of_pdict_fast_groupby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    foos_by_bar = foos.bar.groupby()

    self.assertEqual(foos_by_bar.aslist(),
                     [[{'baz': 3, 'foo': 0, 'bar': 0},
                       {'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'baz': 6, 'foo': 1, 'bar': 1}]])

  def test_plist_of_pdict_groupby_filter_by_eq(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

    foos_by_bar = foos.bar.groupby()

    self.assertEqual((foos_by_bar.bar == 0).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [], []])
    self.assertEqual((foos_by_bar.bar == 1).aslist(),
                     [[], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])
    self.assertEqual((foos_by_bar.bar == 2).aslist(),
                     [[], [], [{'foo': 2, 'bar': 2}]])

  def test_plist_of_pdict_groupby_filter_by_inequalities(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

    foos_by_bar = foos.bar.groupby()

    self.assertEqual((foos_by_bar.bar > 0).aslist(),
                     [[], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], [{'foo': 2, 'bar': 2}]])
    self.assertEqual((foos_by_bar.bar != 1).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [], [{'foo': 2, 'bar': 2}]])
    self.assertEqual((foos_by_bar.bar < 2).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])
    self.assertEqual((foos_by_bar.bar <= 1).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])
    self.assertEqual((foos_by_bar.bar >= 1).aslist(),
                     [[], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], [{'foo': 2, 'bar': 2}]])

  def test_plist_of_pdict_groupby_filter_and_assign(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos_by_bar = foos.bar.groupby()

    baz = foos_by_bar.baz.np_().sum()

    self.assertEqual(baz.aslist(),
                     [[3, 5], [6]])

    max_baz = baz.np().max()

    self.assertEqual(max_baz.aslist(),
                     [[5], [6]])
    self.assertEqual((baz == max_baz).aslist(),
                     [[{'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'baz': 6, 'foo': 1, 'bar': 1}]])

    (baz == max_baz).bin = 13

    self.assertEqual(foos_by_bar.aslist(),
                     [[{'baz': 3, 'foo': 0, 'bar': 0},
                       {'bin': 13, 'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1}]])

  def test_plist_of_pdict_and_filter(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    foos_by_bar = foos.bar.groupby()
    baz = foos_by_bar.baz.np_().sum()
    max_baz = baz.np().max()
    (baz == max_baz).bin = 13

    self.assertEqual(((foos.bar == 0) & (foos.baz == 3)).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])

  def test_plist_of_pdict_groupby_and_filter(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
    foos_by_bar = foos.bar.groupby()

    self.assertEqual(((foos_by_bar.bar == 0) & (foos_by_bar.bar == 1)).aslist(),
                     [[], [], []])
    self.assertEqual(((foos_by_bar.bar == 0) & (foos_by_bar.bar <= 1)).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [], []])

  def test_plist_of_pdict_groupby_or_filter(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
    foos_by_bar = foos.bar.groupby()

    self.assertEqual(((foos_by_bar.bar == 0) | (foos_by_bar.bar == 1)).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])
    self.assertEqual(((foos_by_bar.bar == 0) | (foos_by_bar.bar <= 1)).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])

  def test_plist_of_pdict_groupby_xor_filter(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
    foos_by_bar = foos.bar.groupby()

    self.assertEqual(((foos_by_bar.bar == 0) ^ (foos_by_bar.bar == 1)).aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])
    self.assertEqual(((foos_by_bar.bar == 0) ^ (foos_by_bar.bar <= 1)).aslist(),
                     [[], [{'foo': 1, 'bar': 1}, {'foo': 4, 'bar': 1}], []])

  def test_plist_of_pdict_apply_len(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    foos.baz = 3 - ((foos.bar == 0).foo % 3)

    self.assertEqual(foos.apply(len).aslist(),
                     [3, 3, 3, 3, 3])

  def test_plist_apply_list_arg(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

    baz = lambda foo, bar, l: [foo + bar] + l

    self.assertEqual(foos.foo.apply(baz, foos.bar, [i for i in range(5)]).aslist(),
                     [[0, 0, 1, 2, 3, 4],
                      [2, 0, 1, 2, 3, 4],
                      [4, 0, 1, 2, 3, 4],
                      [3, 0, 1, 2, 3, 4],
                      [5, 0, 1, 2, 3, 4]])

  def test_plist_call_list_arg(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

    foos.baz = lambda foo, bar, l: [foo + bar] + l

    self.assertEqual(foos.baz(foos.foo, foos.bar, [i for i in range(5)]).aslist(),
                     [[0, 0, 1, 2, 3, 4],
                      [2, 0, 1, 2, 3, 4],
                      [4, 0, 1, 2, 3, 4],
                      [3, 0, 1, 2, 3, 4],
                      [5, 0, 1, 2, 3, 4]])

  def test_plist_of_pdict_call_attr_with_name_kwarg(self):
    foos = plist([pdict(foo=lambda name: name, bar=str(i)) for i in range(5)])
    names = foos.foo(name=foos.bar)

    self.assertEqual(names.aslist(),
                     ['0', '1', '2', '3', '4'])

  def test_plist_of_pdict_apply_keys(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    foos.baz = 3 - ((foos.bar == 0).foo % 3)

    self.assertEqual(foos.apply('keys').apply(sorted).aslist(),
                     [['bar', 'baz', 'foo'],
                      ['bar', 'baz', 'foo'],
                      ['bar', 'baz', 'foo'],
                      ['bar', 'baz', 'foo'],
                      ['bar', 'baz', 'foo']])

  def test_plist_of_pdict_groupby_filter_pshape(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
    foos_by_bar = foos.bar.groupby()
    self.assertEqual((foos_by_bar.bar == 0).pshape().aslist(),
                     [[2], [], []])

  def test_plist_of_pdict_groupby_filter_nonempty(self):
    foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
    foos_by_bar = foos.bar.groupby()
    self.assertEqual((foos_by_bar.bar == 0).nonempty().aslist(),
                     [[{'foo': 0, 'bar': 0}, {'foo': 3, 'bar': 0}]])

  def test_plist_of_pdict_tuple_index(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos[('bar', 'baz')].aslist(),
                     [(0, 3), (1, 6), (0, 1), (1, 6), (0, 2)])

  def test_plist_of_pdict_puniq(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.puniq().aslist(),
                     [0, 1])
    self.assertEqual(foos.bar.puniq().root().aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}, {'baz': 6, 'foo': 1, 'bar': 1}])

  def test_plist_of_pdict_puniq(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.puniq().aslist(),
                     [0, 1])
    self.assertEqual(foos.bar.puniq().root().aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}, {'baz': 6, 'foo': 1, 'bar': 1}])

  def test_plist_of_pdict_groupby_tuple_index(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
    self.assertEqual(by_bar_baz[('bar', 'baz')].aslist(),
                     [[[(1, 6), (1, 6)]], [[(0, 1)], [(0, 2)], [(0, 3)]]])

  def test_plist_of_pdict_groupby_puniq(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
    self.assertEqual(by_bar_baz.bar.puniq().aslist(),
                     [[[1]], [[0], [0], [0]]])

    self.assertEqual(by_bar_baz.bar.puniq().root__().aslist(),
                     [[[{'baz': 6, 'foo': 1, 'bar': 1}]],
                      [[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])

  def test_plist_of_pdict_groupby_contains(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6
    (foos.bar == 0).bin = 'abcdefghijklmnopqrstuvwxyz'
    (foos.bar == 1).bin = 'abcdefghijklmnopqrstuvwxyz'[::-1]

    self.assertTrue(6 in foos.baz)
    self.assertFalse('a' in foos)
    self.assertFalse(foos in foos)
    self.assertTrue('abcdefghijklmnopqrstuvwxyz' in foos.bin)

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertTrue(by_bar_baz[0] in by_bar_baz)
    self.assertTrue(6 in by_bar_baz.baz)
    self.assertFalse('a' in by_bar_baz)
    self.assertFalse(by_bar_baz in by_bar_baz)
    self.assertTrue('abcdefghijklmnopqrstuvwxyz' in by_bar_baz.bin)

  def test_plist_of_pdict_slice(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos[:3].aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0}])
    self.assertEqual(foos[:3].bar.aslist(),
                     [0, 1, 0])
    self.assertEqual(foos.bar[:3].aslist(),
                     [0, 1, 0])
    self.assertEqual(foos.bar[:3].root().bar.aslist(),
                     [0, 1, 0])

  def test_plist_of_pdict_sortby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.sortby().aslist(),
                     [0, 0, 0, 1, 1])
    self.assertEqual(foos.bar.sortby(reverse=True).aslist(),
                     [1, 1, 0, 0, 0])

  def test_plist_of_pdict_enum_sortby_root(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual((foos.enum().uproot()._[1].baz - foos.enum().uproot()._[1].bar).sortby().root()._[0].aslist(),
                     [2, 4, 0, 1, 3])
    self.assertEqual((foos.enum().uproot()._[1].baz - foos.enum().uproot()._[1].bar).sortby(reverse=True).root()._[0].aslist(),
                     [1, 3, 0, 4, 2])

    self.assertEqual(foos.bar.enum().uproot()._[1].sortby().root()._[0].aslist(),
                     [0, 2, 4, 1, 3])
    self.assertEqual(foos.bar.enum().uproot()._[1].sortby(reverse=True).root()._[0].aslist(),
                     [1, 3, 0, 2, 4])

  def test_plist_of_pdict_sortby_groupby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.sortby(reverse=True).groupby().aslist(),
                     [[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}],
                      [{'baz': 3, 'foo': 0, 'bar': 0}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}]])

  def test_plist_of_pdict_iops(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    foos.bar += 3
    foos.foo += foos.bar

    self.assertEqual(foos.aslist(),
                     [{'baz': 3, 'foo': 3, 'bar': 3},
                      {'baz': 6, 'foo': 5, 'bar': 4},
                      {'baz': 1, 'foo': 5, 'bar': 3},
                      {'baz': 6, 'foo': 7, 'bar': 4},
                      {'baz': 2, 'foo': 7, 'bar': 3}])

    foos.foo -= foos.bar
    foos.bar -= 3

    self.assertEqual(foos.aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])

    foos.baz *= 2
    foos.foo *= foos.baz

    self.assertEqual(foos.aslist(),
                     [{'baz': 6, 'foo': 0, 'bar': 0},
                      {'baz': 12, 'foo': 12, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0},
                      {'baz': 12, 'foo': 36, 'bar': 1},
                      {'baz': 4, 'foo': 16, 'bar': 0}])

    foos.foo //= foos.baz
    foos.baz //= 2

    self.assertEqual(foos.aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])

  def test_plist_of_pdict_groupby_groupby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    max_baz = baz.np().max()
    (baz == max_baz).bin = 13

    self.assertEqual(by_bar.aslist(),
                     [[{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0}, {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0}, {'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0}],
                      [{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1}, {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}]])
    self.assertEqual(by_bar.bin.groupby().aslist(),
                     [[[{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0}, {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0}],
                       [{'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0}]],
                      [[{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1}, {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}]]])

  def test_plist_of_pdict_sortby_groupby_groupby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.sortby(reverse=True).groupby().baz.groupby().aslist(),
                     [[[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}]],
                      [[{'baz': 3, 'foo': 0, 'bar': 0}],
                       [{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}]]])

  def test_plist_of_pdict_sortby_groupby_groupby_sortby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby().aslist(),
                     [[[3], [1], [2]],
                      [[6, 6]]])

    self.assertEqual(foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby().root().aslist(),
                     [[[{'baz': 3, 'foo': 0, 'bar': 0}], [{'baz': 1, 'foo': 2, 'bar': 0}], [{'baz': 2, 'foo': 4, 'bar': 0}]],
                      [[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}]]])

    self.assertEqual(foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().aslist(),
                     [[[6, 6]],
                      [[1],
                       [2],
                       [3]]])

    self.assertEqual(foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root().aslist(),
                     [[[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}]],
                      [[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])

  def test_plist_of_pdict_groupby_groupby_len(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.apply(len, pepth=0).aslist(),
                     [1, 3])
    self.assertEqual(by_bar_baz.apply(len, pepth=1).aslist(),
                     [[2], [1, 1, 1]])
    self.assertEqual(by_bar_baz.apply(len, pepth=2).aslist(),
                     [[[3, 3]], [[3], [3], [3]]])

  def test_plist_of_pdict_groupby_groupby_plen(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
    by_bar_baz_filtered = by_bar_baz.bar == 0

    self.assertEqual(foos.plen().aslist(),
                     [5])
    self.assertEqual(by_bar_baz.plen().aslist(),
                     [2])
    self.assertEqual(by_bar_baz.plen(1).aslist(),
                     [[4]])
    self.assertEqual(by_bar_baz.plen(-1).aslist(),
                     [[[5]]])
    self.assertEqual(by_bar_baz_filtered.plen().aslist(),
                     [2])
    self.assertEqual(by_bar_baz_filtered.plen(1).aslist(),
                     [[4]])
    self.assertEqual(by_bar_baz_filtered.plen(r=2).aslist(),
                     [[[3]]])

    self.assertEqual(foos.plen(s=1),
                     5)
    self.assertEqual(by_bar_baz.plen(s=1),
                     2)
    self.assertEqual(by_bar_baz.plen_(s=True).aslist(),
                     [1, 3])
    self.assertEqual(by_bar_baz.plen__(s=1).aslist(),
                     [[2], [1, 1, 1]])
    self.assertEqual(by_bar_baz.plen__(s=1),
                     by_bar_baz.plen(s=1, pepth=2))
    self.assertEqual(by_bar_baz_filtered.plen(s=1),
                     2)
    self.assertEqual(by_bar_baz_filtered.plen(1, s=1),
                     4)
    self.assertEqual(by_bar_baz_filtered.plen(r=2, s=1),
                     3)

  def test_plist_of_pdict_groupby_groupby_pshape(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos.pshape().aslist(),
                     [5])
    self.assertEqual(by_bar_baz.pshape().aslist(),
                     [[[2]], [[1], [1], [1]]])
    self.assertEqual(by_bar_baz.pshape_().aslist(),
                     [[[2]], [[1], [1], [1]]])
    self.assertEqual(by_bar_baz.pshape__().aslist(),
                     [[[2]], [[1], [1], [1]]])

  def test_plist_of_pdict_groupby_groupby_pdepth(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
    by_bar_baz_filtered = by_bar_baz.bar == 0

    self.assertEqual(foos.pdepth().aslist(),
                     [0])
    self.assertEqual(by_bar_baz.pdepth().aslist(),
                     [[[2]], [[2], [2], [2]]])
    self.assertEqual(by_bar_baz.pdepth_().aslist(),
                     [[[1]], [[1], [1], [1]]])
    self.assertEqual(by_bar_baz.pdepth__().aslist(),
                     [[[0]], [[0], [0], [0]]])
    self.assertEqual(by_bar_baz.pdepth__().aslist(),
                     by_bar_baz.pdepth(pepth=2).aslist())
    self.assertEqual(by_bar_baz_filtered.pdepth().aslist(),
                     [[[]], [[2], [2], [2]]])

    self.assertEqual(foos.pdepth(1),
                     0)
    self.assertEqual(by_bar_baz.pdepth(s=1),
                     2)
    self.assertEqual(by_bar_baz.pdepth_(True),
                     1)
    self.assertEqual(by_bar_baz.pdepth__(1),
                     0)
    self.assertEqual(by_bar_baz.pdepth__(1),
                     by_bar_baz.pdepth(s=1, pepth=2))
    self.assertEqual(by_bar_baz_filtered.pdepth(s=1),
                     2)

  def test_plist_of_pdict_groupby_groupby_pstructure(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos.pstructure().aslist(),
                     [5])
    self.assertEqual(by_bar_baz.pstructure().aslist(),
                     [2, 4, 5])

  def test_plist_of_pdict_groupby_groupby_pfill(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.pfill().aslist(),
                     [[[0, 1]], [[2], [3], [4]]])
    self.assertEqual(by_bar_baz.pfill(1).aslist(),
                     [[[1, 2]], [[3], [4], [5]]])
    self.assertEqual(by_bar_baz.pfill(6).aslist(),
                     [[[6, 7]], [[8], [9], [10]]])
    self.assertEqual(by_bar_baz.pfill_().aslist(),
                     [[[0, 1]], [[0], [1], [2]]])
    self.assertEqual(by_bar_baz.pfill__().aslist(),
                     [[[0, 1]], [[0], [0], [0]]])
    # Generates a complete index plist into the source plist.
    self.assertEqual(by_bar_baz.apply('pfill', 0, pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])
    # Better way of generating a complete index with pfill.
    self.assertEqual(by_bar_baz.pfill(pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])

  def test_plist_of_pdict_groupby_groupby_lfill(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.lfill(),
                     [[[0, 1]], [[2], [3], [4]]])
    self.assertNotIsInstance(by_bar_baz.lfill(), plist)
    self.assertEqual(by_bar_baz.lfill(1),
                     [[[1, 2]], [[3], [4], [5]]])
    self.assertEqual(by_bar_baz.lfill(6),
                     [[[6, 7]], [[8], [9], [10]]])

    self.assertEqual(by_bar_baz.lfill_().aslist(),
                     [[[0, 1]], [[0], [1], [2]]])
    self.assertIsInstance(by_bar_baz.lfill_(), plist)
    self.assertEqual(by_bar_baz.lfill__().aslist(),
                     [[[0, 1]], [[0], [0], [0]]])

    self.assertEqual(by_bar_baz.lfill__().aslist(),
                     by_bar_baz.lfill(pepth=2).aslist())

    # Generates a complete index list into the source plist.
    self.assertEqual(by_bar_baz.apply('lfill', 0, pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])
    self.assertIsInstance(by_bar_baz.apply('lfill', 0, pepth=-1), plist)

    self.assertEqual(by_bar_baz.apply('lfill', 0, pepth=-1).aslist(),
                     by_bar_baz.lfill(pepth=-1).aslist())

  def test_plist_of_pdict_groupby_groupby_pleft(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.pleft().aslist(),
                     [[[4, 3]], [[2], [1], [0]]])
    self.assertEqual(by_bar_baz.pleft_().aslist(),
                     [[[1, 0]], [[2], [1], [0]]])
    self.assertEqual(by_bar_baz.pleft__().aslist(),
                     [[[1, 0]], [[0], [0], [0]]])

  def test_plist_of_pdict_groupby_groupby_ungroup(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.ungroup().aslist(),
                     [[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}],
                      [{'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}]])
    self.assertEqual(by_bar_baz.ungroup().ungroup().aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}])
    self.assertEqual(by_bar_baz.ungroup(2).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}])
    self.assertEqual(by_bar_baz.ungroup(-1).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}])

  def test_plist_of_pdict_groupby_groupby_ungroup_root(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.ungroup_().root().aslist(),
                     [[[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}]],
                      [[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])
    self.assertEqual(by_bar_baz.ungroup().root().aslist(),
                     [[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}],
                      [{'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}]])

  def test_plist_of_pdict_groupby_groupby_values_like(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.values_like().aslist(),
                     [[[0, 0]], [[0], [0], [0]]])
    self.assertEqual(by_bar_baz.values_like(11).aslist(),
                     [[[11, 11]], [[11], [11], [11]]])
    self.assertEqual(by_bar_baz.values_like_(12).aslist(),
                     [[[12, 12]], [[12], [12], [12]]])
    self.assertEqual(by_bar_baz.ungroup().values_like('a').aslist(),
                     [['a', 'a'], ['a', 'a', 'a']])
    self.assertEqual(by_bar_baz.values_like(by_bar_baz.foo + by_bar_baz.bar).aslist(),
                     [[[2, 4]], [[2], [4], [0]]])

  def test_plist_of_pdict_groupby_apply_psplat(self, psplit=False):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    # by_foo is just foo with an extra plist wrapping each element.
    by_foo = foos.foo.groupby()
    by_foo_psplat = by_foo.apply(lambda x, *a, **kw: qj(x, *a, **kw), psplat=True, psplit=psplit, n=0, b=0, *(None, 0), **dict(t=0, z=0))

    # psplatting by_foo gets rid of the inner plist wrappers, so the result should be the same as foos.
    self.assertEqual(foos.aslist(),
                     by_foo_psplat.aslist())

  def test_plist_of_pdict_groupby_apply_psplat_psplit(self):
    self.test_plist_of_pdict_groupby_apply_psplat(psplit=True)

  def test_plist_of_pdict_groupby_groupby_apply_paslist(self, psplit=False):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    by_bar_baz_apply_paslist = by_bar_baz.apply(lambda x, *a, **kw: qj(x, *a, **kw), paslist=True, psplit=psplit, n=0, b=0, *(None, 0), **dict(t=0, z=0))
    by_bar_baz_apply_paslist_psplat = by_bar_baz.apply(lambda *x, **kw: qj(x, **kw), paslist=True, psplat=True, psplit=psplit, n=0, b=0, **dict(t=0, z=0))

    # This test shows that doing apply(..., paslist=True) may give back a plist with lower depth than the input plist.
    # This is because aslist() has to be fully recursive, but there isn't a true inverse operation that we can know a priori,
    # since the function passed to apply could return an arbitrary structure, so instead it just wraps each returned value
    # as a plist and returns that collection as a plist.
    self.assertEqual(by_bar_baz.aslist(),
                     by_bar_baz_apply_paslist.aslist())
    self.assertEqual(by_bar_baz.pshape().aslist(),
                     [[[2]], [[1], [1], [1]]])
    self.assertEqual(by_bar_baz_apply_paslist.pshape().aslist(),
                     [[1], [3]])

    self.assertEqual(by_bar_baz.aslist(),
                     by_bar_baz_apply_paslist_psplat.aslist())
    self.assertEqual(by_bar_baz_apply_paslist_psplat.pshape().aslist(),
                     [[1], [3]])

  def test_plist_of_pdict_groupby_groupby_apply_paslist_psplit(self):
    self.test_plist_of_pdict_groupby_groupby_apply_paslist(psplit=True)

  def test_plist_of_pdict_groupby_groupby_me_local(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    me = plist()
    ((foos.bar == 0).me()
      .foo.apply(
          self.assertEqual,
          me.foo
      )
    )

    me2 = plist()
    me.bar.me('me2').apply(self.assertEqual, me2)
    me.bar.me('me2').root().baz.apply(self.assertEqual, me2.root().baz)

    (foos.bar.sortby(reverse=True).groupby().baz.groupby()
      .baz.me(me).sortby_().root()
      .apply(
          lambda x, y: (self.assertEqual(x, y) and False) or x,  # Always returns x if there's no exception.
          plist[[[{'foo': 1, 'bar': 1, 'baz': 6},
                  {'foo': 3, 'bar': 1, 'baz': 6}]],
                [[{'foo': 2, 'bar': 0, 'baz': 1}],
                 [{'foo': 4, 'bar': 0, 'baz': 2}],
                 [{'foo': 0, 'bar': 0, 'baz': 3}]]],
          paslist=True
      )
      .root()[-1:].baz
      .apply(
          lambda x, y: (self.assertEqual(x, y) and False) or x,  # Always returns x if there's no exception.
          (me.uproot() < 6).nonempty(-1).sortby_().root(),
          paslist=True
      )
    )

    self.assertEqual(me.aslist(),
                     [[[6, 6]], [[1], [2], [3]]])

  def test_plist_of_pdict_groupby_groupby_me_global(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertFalse('me' in globals())
    self.assertFalse('me2' in globals())

    try:
      # If there's no local variable, me() will create a global variable. Not particularly recommended, but convenient in notebooks.
      ((foos.bar == 0).me()
        .foo.apply(
            self.assertEqual,
            me.foo
        )
      )

      self.assertTrue('me' in globals())

      me.bar.me('me2').apply(self.assertEqual, me2)
      me.bar.me('me2').root().baz.apply(self.assertEqual, me2.root().baz)

      self.assertTrue('me2' in globals())
    finally:
      # Clean up the globals.
      del globals()['me']
      del globals()['me2']

  def test_plist_of_pdict_groupby_groupby_pand(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos.bar.pand().root().baz.pand().aslist(),
                     [(1, 6), (1, 6), (0, 3), (0, 1), (0, 2)])
    self.assertEqual(by_bar_baz.bar.pand('other_pand').root().baz.pand('other_pand').aslist(),
                     [[[(1, 6),
                        (1, 6)]],
                      [[(0, 1)],
                       [(0, 2)],
                       [(0, 3)]]])

    self.assertRaises(ValueError, lambda: foos.bar.pand() and by_bar_baz.bar.pand())

  def test_plist_of_pdict_groupby_groupby_pand_apply_as_args(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    def foo_func(foo, bar, baz):
      assert isinstance(foo, str) and isinstance(bar, float) and isinstance(baz, int)
      return '%s %.2f %d' % (foo, bar, baz)

    me = plist()
    foos_out = by_bar_baz.bar.apply(float, pepth=-1).pand().root().baz.pand().me().root().foo.pstr().apply(lambda x, args: foo_func(x, *args), me, pepth=2)

    self.assertEqual(foos_out.aslist(),
                     [[['1 1.00 6', '3 1.00 6']],
                      [['2 0.00 1'],
                       ['4 0.00 2'],
                       ['0 0.00 3']]])

  def test_plist_of_pdict_groupby_groupby_pand_apply_psplat(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    def foo_func(foo, bar, baz):
      assert isinstance(foo, str) and isinstance(bar, float) and isinstance(baz, int)
      return '%s %.2f %d' % (foo, bar, baz)

    me = plist()
    foos_out = by_bar_baz.foo.pstr().pand().root().bar.apply(float, pepth=-1).pand().root().baz.pand().apply(foo_func, psplat=True, pepth=2)

    self.assertEqual(foos_out.aslist(),
                     [[['1 1.00 6', '3 1.00 6']],
                      [['2 0.00 1'],
                       ['4 0.00 2'],
                       ['0 0.00 3']]])

  def test_plist_of_pdict_groupby_groupby_getitem_list_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos.baz[[0, 1, 2]].aslist(),
                     [6, 6, 3])

    self.assertEqual(by_bar_baz.baz[[0, 1]].aslist(),
                     [[[6, 6]],
                      [[1],
                       [2],
                       [3]]])

    self.assertEqual(by_bar_baz.baz[
                         [[[0, 1]]]
                     ].aslist(),
                     [[[6, 6]]])

    self.assertEqual(by_bar_baz.baz[
                         [[[0, 1]], [[0], [0], [0]]]
                     ].aslist(),
                     [[[6, 6]],
                      [[1],
                       [2],
                       [3]]])

  def test_plist_of_pdict_groupby_groupby_getitem_slice_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos.baz[:3].aslist(),
                     [6, 6, 3])

    self.assertEqual(by_bar_baz.baz[:2].aslist(),
                     [[[6, 6]],
                      [[1],
                       [2],
                       [3]]])

    self.assertEqual(by_bar_baz.baz[:1].aslist(),
                     [[[6, 6]]])

    self.assertEqual(by_bar_baz.baz[[slice(0,2)]].aslist(),
                     [[[6, 6]]])

  def test_plist_of_pdict_groupby_groupby_getitem_tuple_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos[('bar', 'baz')].aslist(),
                     [(1, 6), (1, 6), (0, 3), (0, 1), (0, 2)])

    self.assertEqual(by_bar_baz[('bar', 'baz')].aslist(),
                     [[[(1, 6),
                        (1, 6)]],
                      [[(0, 1)],
                       [(0, 2)],
                       [(0, 3)]]])

  def test_plist_of_pdict_groupby_groupby_getitem_str_list_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # potentially inhomogeneous.
    self.assertEqual(foos[['foo', 'bar', 'baz', 'bar', 'foo']].aslist(),
                     [1, 1, 3, 0, 4])

    self.assertEqual(by_bar_baz[['foo', 'bar']].aslist(),
                     [[[1, 3]],
                      [[0],
                       [0],
                       [0]]])

    self.assertEqual(by_bar_baz[
                         [[['foo', 'baz']]]
                     ].aslist(),
                     [[[1, 6]]])

    self.assertEqual(by_bar_baz[
                         [[['foo', 'baz']], [['foo'], ['bar'], ['baz']]]
                     ].aslist(),
                     [[[1, 6]],
                      [[2],
                       [0],
                       [3]]])

  def test_plist_of_pdict_groupby_groupby_setitem_list_key_simple_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    foos[[0, 1, 2]] = 13

    self.assertEqual(foos.aslist(),
                     [13, 13, 13,
                      {'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

    by_bar_baz[[[[0, 1]]]] = 19

    self.assertEqual(by_bar_baz[[0, 1]].aslist(),
                     [[[19, 19]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

  def test_plist_of_pdict_setitem_list_key_list_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    foos[[0, 1, 2]] = foos[[-1, -2, -3]]

    self.assertEqual(foos.aslist(),
                     [{'foo': 4, 'bar': 0, 'baz': 2},
                      {'foo': 3, 'bar': 1, 'baz': 6},
                      {'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 3, 'bar': 1, 'baz': 6},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

  def test_plist_of_pdict_groupby_groupby_setitem_list_key_list_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(foos[-2:].aslist(),
                     [{'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'foo': 1, 'bar': 1, 'baz': 6},
                        {'foo': 3, 'bar': 1, 'baz': 6}]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

    by_bar_baz[[[[0, 1]]]] = foos[-2:]

    self.assertEqual(by_bar_baz[[0, 1]].aslist(),
                     [[[{'foo': 2, 'bar': 0, 'baz': 1},
                        {'foo': 4, 'bar': 0, 'baz': 2}]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

  def test_plist_of_pdict_groupby_groupby_setitem_slice_key_simple_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    foos[:3] = 13

    self.assertEqual(foos.aslist(),
                     [13, 13, 13,
                      {'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

    by_bar_baz[[[slice(0, 2)]]] = 19

    self.assertEqual(by_bar_baz.aslist(),
                     [[[19, 19]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

  def test_plist_of_pdict_setitem_slice_key_list_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    foos[:3] = [13, 13, 13]

    self.assertEqual(foos.aslist(),
                     [13, 13, 13,
                      {'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

  def test_plist_of_pdict_groupby_groupby_setitem_slice_key_list_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    by_bar_baz[[[slice(0, 2)]]] = [19, 19]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[19, 19]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

  def test_plist_of_pdict_setitem_tuple_key_single_tuple_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    foos[('bar', 'baz')] = (1, 2)

    self.assertEqual(foos[('bar', 'baz')].aslist(),
                     [(1, 2), (1, 2), (1, 2), (1, 2), (1, 2)])

  def test_plist_of_pdict_groupby_groupby_setitem_tuple_key_single_tuple_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    by_bar_baz[('bar', 'baz')] = (1, 2)

    self.assertEqual(by_bar_baz[('bar', 'baz')].aslist(),
                     [[[(1, 2),
                        (1, 2)]],
                      [[(1, 2)],
                       [(1, 2)],
                       [(1, 2)]]])

  def test_plist_of_pdict_setitem_tuple_key_list_tuple_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    foos[('bar', 'baz')] = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

    self.assertEqual(foos[('bar', 'baz')].aslist(),
                     [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])

  def test_plist_of_pdict_groupby_groupby_setitem_tuple_key_list_tuple_val(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    by_bar_baz[('bar', 'baz')] = [[[(1, 2),
                                    (3, 4)]],
                                  [[(5, 6)],
                                   [(7, 8)],
                                   [(9, 10)]]]

    self.assertEqual(by_bar_baz[('bar', 'baz')].aslist(),
                     [[[(1, 2),
                        (3, 4)]],
                      [[(5, 6)],
                       [(7, 8)],
                       [(9, 10)]]])

  def test_plist_of_pdict_setitem_str_list_key_single_value(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # potentially inhomogeneous.
    foos[['foo', 'bar', 'baz', 'bar', 'foo']] = 1

    self.assertEqual(foos[['foo', 'bar', 'baz', 'bar', 'foo']].aslist(),
                     [1, 1, 1, 1, 1])

  def test_plist_of_pdict_groupby_groupby_setitem_str_list_key_single_value(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # potentially inhomogeneous.
    by_bar_baz[['foo', 'bar']] = 1

    self.assertEqual(by_bar_baz[['foo', 'bar']].aslist(),
                     [[[1, 1]],
                      [[1],
                       [1],
                       [1]]])

    by_bar_baz[[[['foo', 'baz']]]] = 2

    self.assertEqual(by_bar_baz[
                         [[['foo', 'baz']]]
                     ].aslist(),
                     [[[2, 2]]])


    by_bar_baz[[[['foo', 'baz']], [['foo'], ['bar'], ['baz']]]] = 3

    self.assertEqual(by_bar_baz[
                         [[['foo', 'baz']], [['foo'], ['bar'], ['baz']]]
                     ].aslist(),
                     [[[3, 3]],
                      [[3],
                       [3],
                       [3]]])

  def test_plist_of_pdict_setitem_str_list_key_list_value(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # potentially inhomogeneous.
    foos[['foo', 'bar', 'baz', 'bar', 'foo']] = [1, 2, 3, 4, 5]

    self.assertEqual(foos[['foo', 'bar', 'baz', 'bar', 'foo']].aslist(),
                     [1, 2, 3, 4, 5])

  def test_plist_of_pdict_groupby_groupby_setitem_str_list_key_list_value(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # potentially inhomogeneous.
    by_bar_baz[['foo', 'bar']] = [1, 2]

    self.assertEqual(by_bar_baz[['foo', 'bar']].aslist(),
                     [[[1, 1]],
                      [[2],
                       [2],
                       [2]]])

    by_bar_baz[[[['foo', 'baz']]]] = [3, 4]

    self.assertEqual(by_bar_baz[
                         [[['foo', 'baz']]]
                     ].aslist(),
                     [[[3, 4]]])


    by_bar_baz[[[['foo', 'baz']], [['foo'], ['bar'], ['baz']]]] = [[[1, 2]], [[3], [4], [5]]]

    self.assertEqual(by_bar_baz[
                         [[['foo', 'baz']], [['foo'], ['bar'], ['baz']]]
                     ].aslist(),
                     [[[1, 2]],
                      [[3],
                       [4],
                       [5]]])

  def test_plist_of_pdict_groupby_groupby_delitem_list_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    del foos[[0, 1, 2]]

    self.assertEqual(foos.aslist(),
                     [{'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

    del by_bar_baz[[[[0, 1]]]]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

  def test_plist_of_pdict_groupby_groupby_delitem_slice_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    del foos[:3]

    self.assertEqual(foos.aslist(),
                     [{'foo': 2, 'bar': 0, 'baz': 1},
                      {'foo': 4, 'bar': 0, 'baz': 2}])

    del by_bar_baz[[[slice(0, 2)]]]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

  def test_plist_of_pdict_delitem_tuple_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    del foos[('bar', 'baz')]

    self.assertEqual(foos.aslist(),
                     [{'foo': 1}, {'foo': 3}, {'foo': 0}, {'foo': 2}, {'foo': 4}])

  def test_plist_of_pdict_groupby_groupby_delitem_tuple_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    del by_bar_baz[('bar', 'baz')]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'foo': 1},
                        {'foo': 3}]],
                      [[{'foo': 2}],
                       [{'foo': 4}],
                       [{'foo': 0}]]])

  def test_plist_of_pdict_delitem_str_list_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # almost certainly inhomogeneous.
    del foos[['foo', 'bar', 'baz', 'bar', 'foo']]

    self.assertEqual(foos.aslist(),
                     [{'bar': 1, 'baz': 6}, {'foo': 3, 'baz': 6}, {'foo': 0, 'bar': 0}, {'foo': 2, 'baz': 1}, {'bar': 0, 'baz': 2}])

  def test_plist_of_pdict_groupby_groupby_delitem_str_list_key(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # This kind of indexing is possible, but it's probably a bad idea to do it, since the resulting object is
    # almost certainly inhomogeneous.
    del by_bar_baz[['foo', 'bar']]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'bar': 1, 'baz': 6},
                        {'bar': 1, 'baz': 6}]],
                      [[{'foo': 2, 'baz': 1}],
                       [{'foo': 4, 'baz': 2}],
                       [{'foo': 0, 'baz': 3}]]])

    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    del by_bar_baz[[[['foo', 'baz']]]]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'bar': 1, 'baz': 6},
                        {'foo': 3, 'bar': 1}]],
                      [[{'foo': 2, 'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'bar': 0, 'baz': 2}],
                       [{'foo': 0, 'bar': 0, 'baz': 3}]]])

    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    del by_bar_baz[[[['foo', 'baz']], [['foo'], ['bar'], ['baz']]]]

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'bar': 1, 'baz': 6},
                        {'foo': 3, 'bar': 1}]],
                      [[{'bar': 0, 'baz': 1}],
                       [{'foo': 4, 'baz': 2}],
                       [{'foo': 0, 'bar': 0}]]])

  def test_plist_of_pdict_groupby_groupby_filter_nonempty(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual((by_bar_baz.bar == 0).nonempty().aslist(),
                     [[[]],
                      [[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])
    self.assertEqual((by_bar_baz.bar == 0).nonempty(2).aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])
    self.assertEqual((by_bar_baz.bar == 0).nonempty(-1).aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])
    self.assertEqual((by_bar_baz.bar == 0).nonempty(-1).nonempty().aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])

  def test_plist_of_pdict_remix(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    self.assertEqual(foos.remix().aslist(),
                     [{}, {}, {}, {}, {}])
    self.assertEqual(foos.remix('foo', 'baz', new_bin=foos.bin * 13).aslist(),
                     [{'foo': 1, 'baz': 6, 'new_bin': 169},
                      {'foo': 3, 'baz': 6, 'new_bin': 169},
                      {'foo': 0, 'baz': 3, 'new_bin': -13},
                      {'foo': 2, 'baz': 5, 'new_bin': -13},
                      {'foo': 4, 'baz': 7, 'new_bin': 169}])

  def test_plist_of_pdict_groupby_remix(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_rm = by_bar.remix('foo', 'baz', new_bin=by_bar.bin * 13)

    self.assertEqual(by_bar.remix().aslist(),
                     [{}, {}])
    self.assertEqual(by_bar_rm.aslist(),
                     [{'foo': [1, 3], 'baz': [6, 6], 'new_bin': [169, 169]},
                      {'foo': [0, 2, 4], 'baz': [3, 5, 7], 'new_bin': [-13, -13, 169]}])
    self.assertEqual(by_bar_rm.baz.aslist(),
                     [[6, 6], [3, 5, 7]])
    self.assertEqual(by_bar_rm.baz.root_().aslist(),
                     [[{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1}, {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}],
                      [{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0}, {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0}, {'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0}]])
    self.assertEqual(by_bar_rm.baz.root_().aslist(),
                     by_bar.aslist())

  def test_plist_of_pdict_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    self.assertEqual(str(foos.pd()),
                     '   bar  baz  bin  foo\n'
                     '0    1    6   13    1\n'
                     '1    1    6   13    3\n'
                     '2    0    3   -1    0\n'
                     '3    0    5   -1    2\n'
                     '4    0    7   13    4')

    self.assertEqual(str(foos.pd(index='foo')),
                     '     bar  baz  bin\n'
                     'foo               \n'
                     '1      1    6   13\n'
                     '3      1    6   13\n'
                     '0      0    3   -1\n'
                     '2      0    5   -1\n'
                     '4      0    7   13')

  def test_plist_of_pdict_groupby_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    self.assertEqual(str(by_bar.baz.pd()),
                     '   0  1    2\n'
                     '0  6  6  NaN\n'
                     '1  3  5  7.0')

  def test_plist_of_pdict_groupby_groupby_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby()

    self.assertEqual(str(by_bar_bin.baz.pd()),
                     '        0     1\n'
                     '0  [6, 6]  None\n'
                     '1  [3, 5]   [7]')

  def test_plist_of_pdict_groupby_remix_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_rm = by_bar.remix('foo', 'baz', new_bin=by_bar.bin * 13)

    self.assertEqual(str(by_bar_rm.pd()),
                     '         baz        foo          new_bin\n'
                     '0     [6, 6]     [1, 3]       [169, 169]\n'
                     '1  [3, 5, 7]  [0, 2, 4]  [-13, -13, 169]')

  def test_plist_of_pdict_groupby_groupby_sortby_pd_inner(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby().bin.sortby__().root()

    self.assertEqual(by_bar_bin.aslist(),
                     [[[{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0},
                        {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0}],
                       [{'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0}]],
                      [[{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1},
                        {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}]]])

    # pylint: disable=bad-continuation
    self.assertEqual(by_bar_bin.pd__().pstr_().aslist(),
                     [[
                          '   bar  baz  bin  foo\n'
                          '0    0    3   -1    0\n'
                          '1    0    5   -1    2',

                          '   bar  baz  bin  foo\n'
                          '0    0    7   13    4',
                      ],
                      [
                          '   bar  baz  bin  foo\n'
                          '0    1    6   13    1\n'
                          '1    1    6   13    3',
                      ]
                     ])
    # pylint: enable=bad-continuation

  def test_plist_of_pdict_groupby_groupby_sortby_ungroup_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby().bin.sortby__().root()

    self.assertEqual(by_bar_bin.ungroup().ungroup().aslist(),
                     [{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0},
                      {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0},
                      {'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0},
                      {'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1},
                      {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}])

    self.assertEqual(str(by_bar_bin.ungroup().ungroup().pd(index='foo')),
                     '     bar  baz  bin\n'
                     'foo               \n'
                     '0      0    3   -1\n'
                     '2      0    5   -1\n'
                     '4      0    7   13\n'
                     '1      1    6   13\n'
                     '3      1    6   13')

  def test_plist_of_pdict_groupby_groupby_sortby_ungroup_custom_sortby_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby().bin.sortby__().root()

    evens_zeros_odds_sort = by_bar_bin.ungroup(2).foo.sortby(
        key=lambda x: (x + 1) * ((x + 1) % 2) - (x + 1) * (x % 2),
        reverse=True).root()

    self.assertEqual(evens_zeros_odds_sort.aslist(),
                     [{'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0},
                      {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0},
                      {'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0},
                      {'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1},
                      {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}])

    self.assertEqual(str(evens_zeros_odds_sort.pd(index='foo')),
                     '     bar  baz  bin\n'
                     'foo               \n'
                     '4      0    7   13\n'
                     '2      0    5   -1\n'
                     '0      0    3   -1\n'
                     '1      1    6   13\n'
                     '3      1    6   13')

    self.assertEqual(str(foos.pd(index='foo')),
                     '     bar  baz  bin\n'
                     'foo               \n'
                     '0      0    3   -1\n'
                     '1      1    6   13\n'
                     '2      0    5   -1\n'
                     '3      1    6   13\n'
                     '4      0    7   13')

  def test_plist_of_pdict_groupby3_ungroup3_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin_baz = by_bar.bin.groupby().baz.groupby()
    self.assertEqual(by_bar_bin_baz.aslist(),
                     [[[[{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0}],
                        [{'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0}]],
                       [[{'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0}]]],
                      [[[{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1},
                         {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}]]]])

    self.assertEqual(by_bar_bin_baz.ungroup(-1).aslist(),
                     [{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0},
                      {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0},
                      {'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0},
                      {'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1},
                      {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}])

    self.assertEqual(str(by_bar_bin_baz.ungroup(-1).pd()),
                     '   bar  baz  bin  foo\n'
                     '0    0    3   -1    0\n'
                     '1    0    5   -1    2\n'
                     '2    0    7   13    4\n'
                     '3    1    6   13    1\n'
                     '4    1    6   13    3')

  def test_plist_of_pdict_pandas_filtering_equivalence(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by = by_bar.ungroup()
    by.idx = range(len(by))

    self.assertEqual(by.aslist(),
                     [{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0, 'idx': 0},
                      {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0, 'idx': 1},
                      {'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0, 'idx': 2},
                      {'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1, 'idx': 3},
                      {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1, 'idx': 4}])

    df = by.pd(index='idx')
    self.assertEqual(str(df),
                     '     bar  baz  bin  foo\n'
                     'idx                    \n'
                     '0      0    3   -1    0\n'
                     '1      0    5   -1    2\n'
                     '2      0    7   13    4\n'
                     '3      1    6   13    1\n'
                     '4      1    6   13    3')

    self.assertEqual(str(df[(df.bar == 0) & (df.bin == -1)]),
                     str(((by.bar == 0) & (by.bin == -1)).pd(index='idx')))

    self.assertEqual(str(df[(df.bar == 0) | (df.bin == -1)]),
                     str(((by.bar == 0) | (by.bin == -1)).pd(index='idx')))

    self.assertEqual(str(df[(df.bar == 0) ^ (df.bin == -1)]),
                     str(((by.bar == 0) ^ (by.bin == -1)).pd(index='idx')))

    self.assertEqual(str(df[(df.bar == 0) & (df.bar == 0)]),
                     str(((by.bar == 0) & (by.bar == 0)).pd(index='idx')))

    self.assertEqual(str(df[(df.bar == 0) & (df.bar == 1)]),
                     str(((by.bar == 0) & (by.bar == 1)).pd(index='idx', columns=sorted(by.keys()[0]))))

  def test_plist_call_with_psplit(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])

    foos.qj_lambda = lambda x, *a, **kw: x.qj(*a, **kw)

    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False

      self.assertEqual(foos.qj_lambda(foos, 'foos', psplit=1, n=0, p=0, *(None, 0), **dict(t=0, z=0)).aslist(),
                       foos.aslist())

      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar_test> <lambda>.lambda: foos <\d+>: \{'bar': 0, 'foo': 0, 'qj_lambda':.*\}")),
              mock.call(
                  RegExp(r"qj: <pstar_test> <lambda>.lambda: foos <\d+>: \{'bar': 1, 'foo': 1, 'qj_lambda':.*\}")),
              mock.call(
                  RegExp(r"qj: <pstar_test> <lambda>.lambda: foos <\d+>: \{'bar': 0, 'foo': 2, 'qj_lambda':.*\}")),
          ],
          any_order=True)
      self.assertEqual(mock_log_fn.call_count, 3)

    qj.LOG_FN = log_fn
    qj.COLOR = True

  def test_plist_call_attr_with_psplit(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])

    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False

      self.assertEqual(foos.qj_('foos', psplit=1, n=0, p=0, *(None, 0), **dict(t=0, z=0)).aslist(),
                       foos.aslist())

      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pool> mapstar: foos <\d+>: \{'bar': 0, 'foo': 0\}")),
              mock.call(
                  RegExp(r"qj: <pool> mapstar: foos <\d+>: \{'bar': 1, 'foo': 1\}")),
              mock.call(
                  RegExp(r"qj: <pool> mapstar: foos <\d+>: \{'bar': 0, 'foo': 2\}")),
          ],
          any_order=True)
      self.assertEqual(mock_log_fn.call_count, 3)

    qj.LOG_FN = log_fn
    qj.COLOR = True

  def test_plist_apply_with_psplit(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])

    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False

      self.assertEqual(foos.apply(qj, 'foos', None, 0, n=0, psplit=1).aslist(),
                       foos.aslist())

      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar> mapstar.lambda: foos <\d+>: \{'bar': 0, 'foo': 0\}")),
              mock.call(
                  RegExp(r"qj: <pstar> mapstar.lambda: foos <\d+>: \{'bar': 1, 'foo': 1\}")),
              mock.call(
                  RegExp(r"qj: <pstar> mapstar.lambda: foos <\d+>: \{'bar': 0, 'foo': 2\}")),
          ],
          any_order=True)
      self.assertEqual(mock_log_fn.call_count, 3)

    qj.LOG_FN = log_fn
    qj.COLOR = True

  def test_plist_of_pdict_inner_qj(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])

    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False

      self.assertEqual(foos.qj_('foos').aslist(),
                       foos.aslist())

      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar_test> test_plist_of_pdict_inner_qj: foos <\d+>: \{'bar': 0, 'foo': 0\}")),
              mock.call(
                  RegExp(r"qj: <pstar_test> test_plist_of_pdict_inner_qj: foos <\d+>: \{'bar': 1, 'foo': 1\}")),
              mock.call(
                  RegExp(r"qj: <pstar_test> test_plist_of_pdict_inner_qj: foos <\d+>: \{'bar': 0, 'foo': 2\}")),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)

    qj.LOG_FN = log_fn
    qj.COLOR = True

  def test_plist_of_pdict_groupby_groupby_apply_args(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby()

    target_calls = by_bar_bin.foo.apply(str, pepth=1)
    self.assertEqual(by_bar_bin.foo.apply_(str),
                     target_calls)

    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False

      by_bar_bin.foo.qj__('CORRECT: foos by_bar_bin')
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> test_plist_of_pdict_groupby_groupby_apply_args: CORRECT: foos by_bar_bin <\d+>: \[0, 2\]')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_plist_of_pdict_groupby_groupby_apply_args: CORRECT: foos by_bar_bin <\d+>: \[4\]')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_plist_of_pdict_groupby_groupby_apply_args: CORRECT: foos by_bar_bin <\d+>: \[1, 3\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.qj('SHOULD MATCH: foos by_bar_bin', pepth=2)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> test_plist_of_pdict_groupby_groupby_apply_args:  SHOULD MATCH: foos by_bar_bin <\d+>: \[0, 2\]')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_plist_of_pdict_groupby_groupby_apply_args:  SHOULD MATCH: foos by_bar_bin <\d+>: \[4\]')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_plist_of_pdict_groupby_groupby_apply_args:  SHOULD MATCH: foos by_bar_bin <\d+>: \[1, 3\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.apply(qj, 'SHOULD MATCH: foos by_bar_bin', pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar> apply: SHOULD MATCH: foos by_bar_bin <\d+>: \[0, 2\]')),
              mock.call(
                  RegExp(r'qj: <pstar> apply: SHOULD MATCH: foos by_bar_bin <\d+>: \[4\]')),
              mock.call(
                  RegExp(r'qj: <pstar> apply: SHOULD MATCH: foos by_bar_bin <\d+>: \[1, 3\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.apply_(qj, 'SHOULD MATCH_: foos by_bar_bin')
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar> apply: SHOULD MATCH_: foos by_bar_bin <\d+>: \[0, 2\]')),
              mock.call(
                  RegExp(r'qj: <pstar> apply: SHOULD MATCH_: foos by_bar_bin <\d+>: \[4\]')),
              mock.call(
                  RegExp(r'qj: <pstar> apply: SHOULD MATCH_: foos by_bar_bin <\d+>: \[1, 3\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.apply(qj, 'PAINFUL *args bin=' + by_bar_bin.bar.apply(str, pepth=2) + ' baz=' + by_bar_bin.baz.apply(str, pepth=2), pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['PAINFUL \*args bin=0 baz=3', 'PAINFUL \*args bin=0 baz=5'\] <\d+>: \[0, 2\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['PAINFUL \*args bin=0 baz=7'\] <\d+>: \[4\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['PAINFUL \*args bin=1 baz=6', 'PAINFUL \*args bin=1 baz=6'\] <\d+>: \[1, 3\]")),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.apply(qj, s='PAINFUL **kwargs bin=' + by_bar_bin.bar.apply(str, pepth=2) + ' baz=' + by_bar_bin.baz.apply(str, pepth=2), pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['PAINFUL \*\*kwargs bin=0 baz=3', 'PAINFUL \*\*kwargs bin=0 baz=5'\] <\d+>: \[0, 2\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['PAINFUL \*\*kwargs bin=0 baz=7'\] <\d+>: \[4\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['PAINFUL \*\*kwargs bin=1 baz=6', 'PAINFUL \*\*kwargs bin=1 baz=6'\] <\d+>: \[1, 3\]")),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.apply(qj, 'NICE *a bin=' + by_bar_bin.bar.pstr() + ' baz=' + by_bar_bin.baz.pstr(), pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['NICE \*a bin=0 baz=3', 'NICE \*a bin=0 baz=5'\] <\d+>: \[0, 2\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['NICE \*a bin=0 baz=7'\] <\d+>: \[4\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['NICE \*a bin=1 baz=6', 'NICE \*a bin=1 baz=6'\] <\d+>: \[1, 3\]")),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

      by_bar_bin.foo.apply(qj, s='NICE **kw bin=' + by_bar_bin.bar.pstr() + ' baz=' + by_bar_bin.baz.pstr(), pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['NICE \*\*kw bin=0 baz=3', 'NICE \*\*kw bin=0 baz=5'\] <\d+>: \[0, 2\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['NICE \*\*kw bin=0 baz=7'\] <\d+>: \[4\]")),
              mock.call(
                  RegExp(r"qj: <pstar> apply: \['NICE \*\*kw bin=1 baz=6', 'NICE \*\*kw bin=1 baz=6'\] <\d+>: \[1, 3\]")),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 3)
      mock_log_fn.reset_mock()

    qj.LOG_FN = log_fn
    qj.COLOR = True

  def test_plist_of_pdict_filter_against_subelements(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])

    self.assertEqual((foos == foos[:1]).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])
    self.assertEqual((foos != foos[:1]).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])

    self.assertEqual((foos == foos[:2]).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1}])
    self.assertEqual((foos != foos[:2]).aslist(),
                     [{'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])

    self.assertEqual((foos == foos[1:2]).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}])
    self.assertEqual((foos != foos[1:2]).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])

    self.assertEqual((foos == foos[1:]).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos != foos[1:]).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])

    self.assertEqual((foos.foo >= foos[:1].foo).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos.foo <= foos[:1].foo).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])

    self.assertEqual((foos.foo >= foos[1:2].foo).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos.foo <= foos[1:2].foo).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1}])

    self.assertEqual((foos.foo >= foos[1:4].foo).aslist(),
                     [{'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos.foo <= foos[1:4].foo).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0},
                      {'baz': 6, 'foo': 1, 'bar': 1}])

    self.assertEqual((foos.foo > foos[:1].foo).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1},
                      {'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos.foo < foos[:1].foo).aslist(),
                     [])

    self.assertEqual((foos.foo > foos[1:2].foo).aslist(),
                     [{'baz': 1, 'foo': 2, 'bar': 0},
                      {'baz': 6, 'foo': 3, 'bar': 1},
                      {'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos.foo < foos[1:2].foo).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])

    self.assertEqual((foos.foo > foos[1:4].foo).aslist(),
                     [{'baz': 2, 'foo': 4, 'bar': 0}])
    self.assertEqual((foos.foo < foos[1:4].foo).aslist(),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])

  def test_plist_of_pdict_groupby_groupby_filter_against_subelements(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby().groupby().baz.sortby_().groupby()

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[{'baz': 6, 'foo': 1, 'bar': 1},
                        {'baz': 6, 'foo': 3, 'bar': 1}]]])

    self.assertEqual((by_bar_baz == by_bar_baz[:1]).aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[]]])
    self.assertEqual((by_bar_baz != by_bar_baz[:1]).aslist(),
                     [[[],
                       [],
                       []],
                      [[{'baz': 6, 'foo': 1, 'bar': 1},
                        {'baz': 6, 'foo': 3, 'bar': 1}]]])

    self.assertEqual((by_bar_baz == by_bar_baz[:2]).aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[{'baz': 6, 'foo': 1, 'bar': 1},
                        {'baz': 6, 'foo': 3, 'bar': 1}]]])
    self.assertEqual((by_bar_baz != by_bar_baz[:2]).aslist(),
                     [[], []])

    self.assertEqual((by_bar_baz.foo >= by_bar_baz[:1].foo).aslist(),
                     [[[],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       []],
                      [[]]])
    self.assertEqual((by_bar_baz.foo <= by_bar_baz[:1].foo).aslist(),
                     [[[],
                       [],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[]]])

    # These two result in element-wise comparison because the two plists have
    # the same base dimension (2).
    self.assertEqual((by_bar_baz.foo >= by_bar_baz[:2].foo).aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[{'baz': 6, 'foo': 1, 'bar': 1},
                        {'baz': 6, 'foo': 3, 'bar': 1}]]])
    self.assertEqual((by_bar_baz.foo <= by_bar_baz[:2].foo).aslist(),
                     [[[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[{'baz': 6, 'foo': 1, 'bar': 1},
                        {'baz': 6, 'foo': 3, 'bar': 1}]]])

  def test_plist_of_pdict_call_elements(self):
    foos = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby().groupby().baz.sortby(pepth=1).groupby()

    self.assertEqual(by_bar_baz.aslist(),
                     [[[{'bin': '4', 'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'bin': '16', 'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'bin': '0', 'baz': 3, 'foo': 0, 'bar': 0}]],
                      [[{'bin': '1', 'baz': 6, 'foo': 1, 'bar': 1},
                        {'bin': '9', 'baz': 6, 'foo': 3, 'bar': 1}]]])

    self.assertEqual(by_bar_baz.bin.pshape().aslist(),
                     [[[1],
                       [1],
                       [1]],
                      [[2]]])

    self.assertEqual(by_bar_baz.bin.replace('1', 'fun').aslist(),
                     [[['4'],
                       ['fun6'],
                       ['0']],
                      [['fun', '9']]])

    self.assertEqual(by_bar_baz.bin.replace('1', by_bar_baz.baz.pstr() * 2).aslist(),
                     [[['4'],
                       ['226'],
                       ['0']],
                      [['66', '9']]])

  def test_plist_of_pdict_groupby_groupby_call_elements(self):
    foos = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby().groupby().baz.sortby(pepth=1).groupby()

    self.assertEqual(by_bar_baz.apply_('__getslice___', 0, 2),
                     [[[{'bin': '4', 'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'bin': '16', 'baz': 2, 'foo': 4, 'bar': 0}]],
                      [[{'bin': '1', 'baz': 6, 'foo': 1, 'bar': 1},
                        {'bin': '9', 'baz': 6, 'foo': 3, 'bar': 1}]]])

    self.assertEqual(by_bar_baz.apply_('__getslice___', 0, 2),
                     by_bar_baz.__getslice__(0, 2, pepth=1))

  def test_sample_data_analysis_flow(self):
    foos = plist([pdict(foo=i, bar=i % 2, bin=i % 13, bun=i % 11) for i in range(1001)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    fields = ('bin', 'bar')
    by = foos[fields].sortby().groupby().bun.sortby(pepth=-1).groupby()
    by.baz = by.foo % (by.bin + by.bun + 1)

    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      qj.COLOR = False

      rmx = by.ungroup(-1).remix('bun', bam=by.baz.np__().mean().ungroup(-1), *fields).bun.sortby().groupby()[fields].sortby().root()

      rmx.bam.qj(rmx.bun.ungroup(-1).puniq().pstr().qj('bun'), n=1, pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar_test> test_sample_data_analysis_flow: bun <\d+>: \['10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0'\]")),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:  10 \(shape \(min \(mean std\) max\) hist\) <\d+>: \(\(91,\), \(0\.0, \(8\.4\d*, 5\.0\d*\), 21\.0\), array\(\[22, 23, 29, 11,  6\]\)')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:  9 \(shape \(min \(mean std\) max\) hist\) <\d+>: \(\(91,\), \(0\.0, \(8.3\d+, 5.1\d+\), 20.0\), array\(\[24, 12, 34, 14,  7\]\)')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 12)
      mock_log_fn.reset_mock()

      (rmx.bam == rmx.bam.np().max())[tuple(['bun'] + list(fields))].qj('max-yielding params').pshape().qj('maxes ps').root()
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:   max-yielding params <\d+>: \[\[\(10, 11, 1\), \(10, 11, 1\), \(10, 11, 1\)\], ')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:    maxes ps <\d+>: \[\[3\], \[5\], \[1\], \[2\], \[1\], \[1\], \[2\], \[1\], \[1\], \[1\], \[7\]\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 2)
      mock_log_fn.reset_mock()

      rmx_x = rmx.bun.puniq(pepth=1).ungroup().qj('rmx_x')
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:     rmx_x <\d+>: \[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 1)
      mock_log_fn.reset_mock()

      rmx.ungroup(-1).bun.groupby().bam.wrap().np_().apply(lambda y, x: [qj((x_, np.mean(y_))) for x_, y_ in zip(x, y)], rmx_x)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> .*: x_, np.mean\(y_\) <\d+>: \(10, 8.4\d+\)')),
              mock.call(
                  RegExp(r'qj: <pstar_test> .*: x_, np.mean\(y_\) <\d+>: \(9, 8.3\d+\)')),
              mock.call(
                  RegExp(r'qj: <pstar_test> .*: x_, np.mean\(y_\) <\d+>: \(8, 7.3\d+\)')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 11)
      mock_log_fn.reset_mock()

      if sys.version_info[0] < 3:
        (rmx.ungroup(-1)[fields].sortby().root().bun.groupby()
         .bam.np_().max().sortby_(reverse=True).np().uproot().shape.qj('shape').root()
         .np().mean().qj('means').wrap().apply(
             lambda y, x: [qj((x_, y_)) for x_, y_ in zip(x, y)], rmx_x
         )
         .root()[0].root().apply('__getslice___', 0, 10).qj('bam top 10').wrap()
         .root()[0].root().__getslice___(0, 10).qj('bam top 10').wrap()
         .root()[0].root().__getslice__(0, 10, pepth=1).qj('bam top 10').wrap()
         .root()[0].root().apply(type).qj('bam types')
        )
      else:
        (rmx.ungroup(-1)[fields].sortby().root().bun.groupby()
         .bam.np_().max().sortby_(reverse=True).np().uproot().shape.qj('shape').root()
         .np().mean().qj('means').wrap().apply(
             lambda y, x: [qj((x_, y_)) for x_, y_ in zip(x, y)], rmx_x
         )
         .root()[0].root().apply('__getitem___', slice(0, 10)).qj('bam top 10').wrap()
         .root()[0].root().__getitem___(slice(0, 10)).qj('bam top 10').wrap()
         .root()[0].root().__getitem__(slice(0, 10), pepth=1).qj('bam top 10').wrap()
         .root()[0].root().apply(type).qj('bam types')
        )

      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:      shape <\d+>: \[\(91,\), \(91,\), \(91,\), \(91,\), \(91,\), \(91,\), \(91,\), \(91,\), \(91,\), \(91,\), \(91,\)\]')),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:       means <\d+>: \[8.4\d+, 8.3\d+, 7.3\d+, 6.1\d+, 6.6\d+, 5.8\d+, 5.0\d+, 4.8\d+, 4.0\d+, 3.7\d+, 3.2\d+\]')),
              mock.call(
                  RegExp(r'qj: <pstar_test> .*: x_, y_ <\d+>: \(10, 8.4\d+\)')),
              mock.call(
                  RegExp(r'qj: <pstar_test> .*: x_, y_ <\d+>: \(9, 8.3\d+\)')),
              mock.call(
                  RegExp(r'qj: <pstar_test> .*: x_, y_ <\d+>: \(8, 7.3\d+\)')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 17)
      mock_log_fn.reset_mock()

    qj.LOG_FN = log_fn

  def test_plist_of_pdict_groupby_groupby_noncallable_attrs(self):
    foos = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby().groupby().baz.sortby(pepth=1).groupby()

    self.assertEqual(foos.__class__,
                     plist)
    self.assertIs(foos.__root__,
                  foos)
    self.assertIn('`list` subclass',
                  foos.__doc__)
    self.assertEqual(foos.__module__,
                     'pstar.pstar')

    self.assertEqual(by_bar_baz.__class__,
                     plist)
    self.assertIs(by_bar_baz.__root__,
                  by_bar_baz)
    self.assertIn('`list` subclass',
                  by_bar_baz.__doc__)
    self.assertEqual(by_bar_baz.__module__,
                     'pstar.pstar')

    self.assertEqual(by_bar_baz.__class___.aslist(),
                     [plist, plist])
    self.assertEqual(by_bar_baz.__class____.aslist(),
                     [[plist, plist, plist], [plist]])
    self.assertEqual(by_bar_baz.__class_____.aslist(),
                     [[[pdict], [pdict], [pdict]], [[pdict, pdict]]])

  def test_plist_generators(self):
    foos = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5)])
    gen_foos = plist(pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5))

    self.assertEqual(foos.aslist(),
                     gen_foos.aslist())

  def test_plist_enum(self):
    foos = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5)])

    self.assertEqual(foos.enum().aslist(),
                     [(0, {'bar': 0, 'bin': '0', 'foo': 0}),
                      (1, {'bar': 1, 'bin': '1', 'foo': 1}),
                      (2, {'bar': 0, 'bin': '4', 'foo': 2}),
                      (3, {'bar': 1, 'bin': '9', 'foo': 3}),
                      (4, {'bar': 0, 'bin': '16', 'foo': 4})])

  def test_plist_zip(self):
    foos0 = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5)])
    (foos0.bar == 0).baz = 3 - ((foos0.bar == 0).foo % 3)
    (foos0.bar == 1).baz = 6

    foos1 = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(5, 10)])
    (foos1.bar == 0).baz = 3 - ((foos1.bar == 0).foo % 3)
    (foos1.bar == 1).baz = 6

    foos2 = plist([pdict(foo=i, bar=i % 2, bin=str(i ** 2)) for i in range(10, 15)])
    (foos2.bar == 0).baz = 3 - ((foos2.bar == 0).foo % 3)
    (foos2.bar == 1).baz = 6

    self.assertEqual(foos0.foo.zip(foos1.foo).aslist(),
                     [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)])

    self.assertEqual(foos0.foo.zip(foos1.foo, foos2.foo).aslist(),
                     [(0, 5, 10), (1, 6, 11), (2, 7, 12), (3, 8, 13), (4, 9, 14)])

    by_bar_baz0 = foos0.bar.sortby().groupby().baz.sortby(pepth=1).groupby()

    by_bar_baz1 = foos0.bar.sortby().groupby().baz.sortby(pepth=1).groupby()
    by_bar_baz1.bar += 1

    by_bar_baz2 = foos0.bar.sortby().groupby().baz.sortby(pepth=1).groupby()
    by_bar_baz2.baz += 1

    self.assertEqual(by_bar_baz0.foo.zip(by_bar_baz1.bar, by_bar_baz2.baz).aslist(),
                     [[[(2, 1, 2)],
                       [(4, 1, 3)],
                       [(0, 1, 4)]],
                      [[(1, 2, 7), (3, 2, 7)]]])

  @unittest.skip('slow')
  def test_z_fast_parallel_file_processing(self):
    tdir = tempfile.mkdtemp()
    try:
      qj(tic=1)
      files = 'test_' + plist([str(i) for i in range(5000)]) + '.txt'
      files = files.values_like(tdir).apply(os.path.join, files)
      with files.apply(open, 'w', psplit=25) as wf:
        wf.write(files, psplit=1)
      with files.apply(open, 'r', psplit=25) as rf:
        contents = rf.read(psplit=1)
      qj(toc=-1)

      self.assertEqual(files.aslist(),
                       contents.aslist())
    finally:
      shutil.rmtree(tdir, ignore_errors=True)

  @unittest.skip('slow')
  def test_z_plist_of_pdict_timing(self):
    qj(tic=1, toc=1)
    large_input = [pdict(foo=i, bar=i % 2, bin=i % 13, bun=i % 11) for i in range(100000)]
    qj(tic=1, toc=1)

    foos = plist(large_input)
    qj(tic=1, toc=1)

    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    qj(tic=1, toc=1)
    (foos.bar == 1).baz = 6
    qj(tic=1, toc=1)

    fields = ('bin', 'bar')
    by = foos[fields].sortby().groupby().bun.sortby_().groupby()
    qj(tic=1, toc=1)
    by.baz = by.foo % (by.bin + by.bun + 1)
    qj(tic=1, toc=1)

    by.baz.qj(by[fields].puniq().ungroup().pstr(), n=10, pepth=2)
    qj(tic=1, toc=1)

  #############################################################################
  # Tests added from documentation.
  #############################################################################
  
  def test_from_docs_pstar(self):
    from pstar import defaultpdict, frozenpset, pdict, plist, pset, ptuple, pstar
    from pstar import pstar
    pd = pstar.pdict(foo=1, bar=2, baz=3)
    pl = pstar.plist([1, 2, 3])


  def test_from_docs_pstar_defaultpdict(self):
    pd = defaultpdict()
    pd.foo = 1
    self.assertTrue(pd['foo'] == pd.foo == 1)
    pd = defaultpdict(int)
    self.assertTrue(pd.foo == 0)
    pd = defaultpdict(foo=1, bar=2)
    self.assertTrue(pd[['foo', 'bar']].aslist() == [1, 2])
    pd = defaultpdict()
    pd[['foo', 'bar']] = 1
    self.assertTrue(pd[['foo', 'bar']].aslist() == [1, 1])
    pd[['foo', 'bar']] = [1, 2]
    self.assertTrue(pd[['foo', 'bar']].aslist() == [1, 2])
    pd = defaultpdict(foo=1, bar=2)
    pd.update(bar=3).baz = 4
    self.assertTrue(pd.bar == 3)
    self.assertTrue('baz' in pd.keys())
    pd = defaultpdict(lambda: defaultpdict(list))
    pd.foo = 1
    pd.stats.bar.append(2)
    self.assertTrue(pd['foo'] == 1)
    self.assertTrue(pd.stats.bar == [2])
    d1 = defaultdict(int, {'foo': 1, 'bar': 2})
    pd = defaultpdict * d1
    self.assertTrue(type(d1) == defaultdict)
    self.assertTrue(type(pd) == defaultpdict)
    self.assertTrue(pd == d1)
    d2 = pd / defaultpdict
    self.assertTrue(type(d2) == defaultdict)
    self.assertTrue(d2 == d1)


  def test_from_docs_pstar_defaultpdict___getattr__(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.foo == 1)
    self.assertTrue(pd.__module__.startswith('pstar'))


  def test_from_docs_pstar_defaultpdict___getitem__(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd['foo'] == pd.foo == 1)
    self.assertTrue(pd[['foo', 'bar', 'baz']].aslist() == [1, 2.0, 'three'])
    self.assertTrue(pd[['foo', 'baz']].root().aslist() ==
            [('foo', 1), ('baz', 'three')])
    self.assertTrue(pd[['foo', 'baz']].pdict() ==
            dict(foo=1, baz='three'))


  def test_from_docs_pstar_defaultpdict___init__(self):
    pd = defaultpdict(int)
    self.assertTrue(pd.foo == 0)
    pd.bar += 10
    self.assertTrue(pd.bar == 10)
    pd = defaultpdict(lambda: defaultpdict(list))
    pd.foo.bar = 20
    self.assertTrue(pd == dict(foo=dict(bar=20)))
    pd.stats.bar.append(2)
    self.assertTrue(pd.stats.bar == [2])


  def test_from_docs_pstar_defaultpdict___setattr__(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    pd.floo = 4.0
    self.assertTrue(pd.floo == pd['floo'] == 4.0)


  def test_from_docs_pstar_defaultpdict___setitem__(self):
    pd = defaultpdict(int)
    pd['foo'] = 1
    self.assertTrue(pd.foo == pd['foo'] == 1)
    pd[['bar', 'baz']] = plist[2.0, 'three']
    self.assertTrue(pd.bar == pd['bar'] == 2.0)
    self.assertTrue(pd.baz == pd['baz'] == 'three')


  def test_from_docs_pstar_defaultpdict___str__(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(str(pd) ==
            "{'bar': 2.0, 'baz': 'three', 'foo': 1}")


  def test_from_docs_pstar_defaultpdict_copy(self):
    pd1 = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    pd2 = pd1.copy()
    self.assertTrue(pd2 == pd1)
    self.assertTrue(pd2 is not pd1)


  def test_from_docs_pstar_defaultpdict_palues(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.palues().aslist() ==
            [2.0, 'three', 1])
    pd_str = (pd.palues().pstr() + ' foo').pdict()
    self.assertTrue(pd_str ==
            dict(foo='1 foo', bar='2.0 foo', baz='three foo'))


  def test_from_docs_pstar_defaultpdict_peys(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.peys().aslist() == ['bar', 'baz', 'foo'])
    pd_str = pdict()
    pd_str[pd.peys()] = pd.palues().pstr()  # Converts the values to strings.
    self.assertTrue(pd_str ==
            dict(foo='1', bar='2.0', baz='three'))


  def test_from_docs_pstar_defaultpdict_pitems(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.pitems().aslist() ==
            [('bar', 2.0), ('baz', 'three'), ('foo', 1)])
    self.assertTrue(pd.pitems().key.aslist() ==
            pd.peys().aslist())
    self.assertTrue(pd.pitems().value.aslist() ==
            pd.palues().aslist())


  def test_from_docs_pstar_defaultpdict_qj(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
      pd.qj('pd').update(baz=3).qj('pd now')
      self.assertTrue(pd.baz == 3)
      # Logs:
      # qj: <calling_module> calling_function: pd <2910>: {'bar': 2.0, 'baz': 'three', 'foo': 1}
      # qj: <calling_module> calling_function:  pd now <2910>: {'bar': 2.0, 'baz': 3, 'foo': 1}
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_defaultpdict_rekey(self):
    pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.rekey(foo='floo') ==
            dict(floo=1, bar=2.0, baz='three'))
    self.assertTrue(pd.foo == 1)  # pd is unmodified by default.
    pd.rekey(dict(bar='car'), True)
    self.assertTrue('bar' not in pd)
    self.assertTrue(pd.car == 2.0)
    pd.rekey(lambda k: 'far' if k == 'car' else k, True)
    self.assertTrue('car' not in pd)
    self.assertTrue(pd.far == 2.0)


  def test_from_docs_pstar_defaultpdict_update(self):
    pd = defaultpdict(int)
    self.assertTrue(pd.update(foo=1, bar=2.0).foo == 1)
    self.assertTrue(pd.bar == 2.0)
    self.assertTrue(pd.update({'baz': 'three'}).baz == 'three')


  def test_from_docs_pstar_frozenpset(self):
    ps = frozenpset([1, 2.0, 'three'])
    ps = frozenpset({1, 2.0, 'three'})
    ps = frozenpset[1, 2.0, 'three']
    s1 = frozenset([1, 2.0, 'three'])
    ps = frozenpset * s1
    self.assertTrue(type(s1) == frozenset)
    self.assertTrue(type(ps) == frozenpset)
    self.assertTrue(ps == s1)
    s2 = ps / frozenpset
    self.assertTrue(type(s2) == frozenset)
    self.assertTrue(s2 == s1)


  def test_from_docs_pstar_frozenpset_qj(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      ps = frozenpset([1, 2.0, 'three'])
      ps.qj('ps')
      # Logs:
      # qj: <calling_module> calling_function: ps <2910>: frozenpset({1, 2.0, 'three'})
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_pdict(self):
    pd = pdict()
    pd.foo = 1
    self.assertTrue(pd['foo'] == pd.foo == 1)
    pd = pdict(foo=1, bar=2)
    self.assertTrue(pd[['foo', 'bar']].aslist() == [1, 2])
    pd = pdict()
    pd[['foo', 'bar']] = 1
    self.assertTrue(pd[['foo', 'bar']].aslist() == [1, 1])
    pd[['foo', 'bar']] = [1, 2]
    self.assertTrue(pd[['foo', 'bar']].aslist() == [1, 2])
    pd = pdict(foo=1, bar=2)
    pd.update(bar=3).baz = 4
    self.assertTrue(pd.bar == 3)
    self.assertTrue('baz' in pd.keys())
    self.assertTrue(pd.baz == 4)
    d1 = {'foo': 1, 'bar': 2}
    pd = pdict * d1
    self.assertTrue(type(d1) == dict)
    self.assertTrue(type(pd) == pdict)
    self.assertTrue(pd == d1)
    d2 = pd / pdict
    self.assertTrue(type(d2) == dict)
    self.assertTrue(d2 == d1)


  def test_from_docs_pstar_pdict___getitem__(self):
    pd = pdict(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd['foo'] == pd.foo == 1)
    self.assertTrue(pd[['foo', 'bar', 'baz']].aslist() == [1, 2.0, 'three'])
    self.assertTrue(pd[['foo', 'baz']].root().aslist() ==
            [('foo', 1), ('baz', 'three')])
    self.assertTrue(pd[['foo', 'baz']].pdict() ==
            dict(foo=1, baz='three'))


  def test_from_docs_pstar_pdict___init__(self):
    pd1 = pdict(foo=1, bar=2.0, baz='three')
    pd2 = pdict({'foo': 1, 'bar': 2.0, 'baz': 'three'})
    self.assertTrue(pd1 == pd2)


  def test_from_docs_pstar_pdict___setitem__(self):
    pd = pdict()
    pd['foo'] = 1
    self.assertTrue(pd.foo == pd['foo'] == 1)
    pd[['bar', 'baz']] = plist[2.0, 'three']
    self.assertTrue(pd.bar == pd['bar'] == 2.0)
    self.assertTrue(pd.baz == pd['baz'] == 'three')


  def test_from_docs_pstar_pdict___str__(self):
    pd = pdict(foo=1, bar=2.0, baz='three')
    self.assertTrue(str(pd) ==
            "{'bar': 2.0, 'baz': 'three', 'foo': 1}")


  def test_from_docs_pstar_pdict_copy(self):
    pd1 = pdict(foo=1, bar=2.0, baz='three')
    pd2 = pd1.copy()
    self.assertTrue(pd2 == pd1)
    self.assertTrue(pd2 is not pd1)


  def test_from_docs_pstar_pdict_palues(self):
    pd = pdict(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.palues().aslist() ==
            [2.0, 'three', 1])
    pd_str = (pd.palues().pstr() + ' foo').pdict()
    self.assertTrue(pd_str ==
            dict(foo='1 foo', bar='2.0 foo', baz='three foo'))


  def test_from_docs_pstar_pdict_peys(self):
    pd = pdict(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.peys().aslist() == ['bar', 'baz', 'foo'])
    pd_str = pdict()
    pd_str[pd.peys()] = pd.palues().pstr()  # Converts the values to strings.
    self.assertTrue(pd_str ==
            dict(foo='1', bar='2.0', baz='three'))


  def test_from_docs_pstar_pdict_pitems(self):
    pd = pdict(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.pitems().aslist() ==
            [('bar', 2.0), ('baz', 'three'), ('foo', 1)])
    self.assertTrue(pd.pitems().key.aslist() ==
            pd.peys().aslist())
    self.assertTrue(pd.pitems().value.aslist() ==
            pd.palues().aslist())


  def test_from_docs_pstar_pdict_qj(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      pd = pdict(foo=1, bar=2.0, baz='three')
      pd.qj('pd').update(baz=3).qj('pd now')
      self.assertTrue(pd.baz == 3)
      # Logs:
      # qj: <calling_module> calling_function: pd <2910>: {'bar': 2.0, 'baz': 'three', 'foo': 1}
      # qj: <calling_module> calling_function:  pd now <2910>: {'bar': 2.0, 'baz': 3, 'foo': 1}
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_pdict_rekey(self):
    pd = pdict(foo=1, bar=2.0, baz='three')
    self.assertTrue(pd.rekey(foo='floo') ==
            dict(floo=1, bar=2.0, baz='three'))
    self.assertTrue(pd.foo == 1)  # pd is unmodified by default.
    pd.rekey(dict(bar='car'), True)
    self.assertTrue('bar' not in pd)
    self.assertTrue(pd.car == 2.0)
    pd.rekey(lambda k: 'far' if k == 'car' else k, True)
    self.assertTrue('car' not in pd)
    self.assertTrue(pd.far == 2.0)


  def test_from_docs_pstar_pdict_update(self):
    pd = pdict()
    self.assertTrue(pd.update(foo=1, bar=2.0).foo == 1)
    self.assertTrue(pd.bar == 2.0)
    self.assertTrue(pd.update({'baz': 'three'}).baz == 'three')


  def test_from_docs_pstar_plist(self):
    pl = plist['abc', 'def', 'ghi']
    self.assertTrue((pl + ' -> ' + pl.upper()).aslist() ==
            ['abc -> ABC', 'def -> DEF', 'ghi -> GHI'])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    # Basic scalar indexing:
    self.assertTrue(foos[0] ==
            dict(foo=0, bar=0))
    # plist slice indexing:
    self.assertTrue(foos[:2].aslist() ==
            [dict(foo=0, bar=0), dict(foo=1, bar=1)])
    # plist int list indexing:
    self.assertTrue(foos[[0, 2]].aslist() ==
            [dict(foo=0, bar=0), dict(foo=2, bar=0)])
    # Basic scalar indexing:
    self.assertTrue(foos['foo'].aslist() ==
            [0, 1, 2])
    # tuple indexing
    self.assertTrue(foos[('foo', 'bar')].aslist() ==
            [(0, 0), (1, 1), (2, 0)])
    # list indexing
    self.assertTrue(foos[['foo', 'bar', 'bar']].aslist() ==
            [0, 1, 0])
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    # Basic scalar indexing:
    self.assertTrue(pl._[0].aslist() ==
            [1, 4, 7])
    # slice indexing (note the use of the 3-argument version of slicing):
    self.assertTrue(pl._[:2:1].aslist() ==
            [[1, 2], [4, 5], [7, 8]])
    # list indexing:
    pl = pl.np()
    self.assertTrue(pl._[[True, False, True]].apply(list).aslist() ==
            [[1, 3], [4, 6], [7, 9]])
    pl = plist[1, 2, 3]
    # `plist` operations don't modify the original (except where natural)!
    self.assertTrue((pl + 5) is not pl)
    self.assertTrue((pl + 5).root() is pl)
    pl2 = pl + 5
    self.assertTrue(pl2.root() is not pl2)
    self.assertTrue(pl2.uproot().root() is pl2)
    self.assertTrue(pl2.root() is pl2)
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    # Filtering on a property:
    zero_bars = foos.bar == 0
    # The result is a `plist` of the original `pdict`s, correctly filtered:
    self.assertTrue(zero_bars.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    # filter can take any function to filter by, but it defaults to bool():
    nonzero_bars = foos.bar.filter()
    self.assertTrue(nonzero_bars.aslist() ==
            [{'foo': 1, 'bar': 1}])
    foos = plist([pdict(foo=0, bar=1), pdict(foo=1, bar=0), pdict(foo=2, bar=1)])
    # Note that the `bar == 1` group comes before the `bar == 0` group. The ordering
    # is determined by the sort order of the `plist`.
    self.assertTrue(foos.bar.groupby().aslist() ==
            [[{'bar': 1, 'foo': 0}, {'bar': 1, 'foo': 2}], [{'bar': 0, 'foo': 1}]])
    # Note that foos is unchanged:
    self.assertTrue(foos.aslist() ==
            [{'bar': 1, 'foo': 0}, {'bar': 0, 'foo': 1}, {'bar': 1, 'foo': 2}])
    self.assertTrue(foos.bar.sortby().aslist() ==
            [0, 1, 1])
    self.assertTrue(foos.aslist() ==
            [{'bar': 0, 'foo': 1}, {'bar': 1, 'foo': 0}, {'bar': 1, 'foo': 2}])
    foos = plist([pdict(foo=0, bar=1), pdict(foo=1, bar=0), pdict(foo=2, bar=1)])
    self.assertTrue(foos.bar.sortby().groupby().aslist() ==
            [[{'bar': 0, 'foo': 1}], [{'bar': 1, 'foo': 0}, {'bar': 1, 'foo': 2}]])
    pl = plist['abc', 'def', 'ghi']
    self.assertTrue(pl.apply('foo: {}'.format).aslist() ==
            ['foo: abc', 'foo: def', 'foo: ghi'])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos.baz = 'abc' * foos.foo
    # Do a multi-argument string format with plist.apply:
    self.assertTrue(foos.foo.apply('foo: {} bar: {} baz: {baz}'.format, foos.bar, baz=foos.baz).aslist() ==
            ['foo: 0 bar: 0 baz: ', 'foo: 1 bar: 1 baz: abc', 'foo: 2 bar: 0 baz: abcabc'])
    # Do the same string format directly using the plist as the format string:
    self.assertTrue(('foo: ' + foos.foo.pstr() + ' bar: {} baz: {baz}').format(foos.bar, baz=foos.baz).aslist() ==
            ['foo: 0 bar: 0 baz: ', 'foo: 1 bar: 1 baz: abc', 'foo: 2 bar: 0 baz: abcabc'])


  def test_from_docs_pstar_plist__(self):
    pl = plist([np.arange(10) for _ in range(3)])
    self.assertTrue(pl._[2].aslist() ==
            [2, 2, 2])
    import operator as op
    self.assertTrue(pl._[2:4:1].apply(op.eq,
                              [np.array([2, 3]), np.array([2, 3]), np.array([2, 3])])
                       .apply(np.all).aslist() ==
            [True, True, True])
    pl = plist([['foo'], ['bar']])
    pl._.append('baz')
    self.assertTrue(pl.apply(type).aslist() ==
            [list, list])
    self.assertTrue(pl.aslist() ==
            [['foo', 'baz'], ['bar', 'baz']])


  def test_from_docs_pstar_plist___call__(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    # A plist of callables, one for each pdict:
    foos_peys = foos.peys
    self.assertTrue(foos_peys.all(callable))
    # The actual call to plist.__call__ (separated out for demonstration):
    self.assertTrue(foos_peys().aslist() ==
            [['bar', 'foo'], ['bar', 'foo'], ['bar', 'foo']])
    # Of course, you would normally do the above like this, which is the same:
    self.assertTrue(foos.peys().aslist() ==
            [['bar', 'foo'], ['bar', 'foo'], ['bar', 'foo']])
    by_bar = foos.bar.groupby()
    # There's rarely any need to pass pepth, as the call gets routed to the
    # correct object by default in almost all situations, even with grouped
    # plists:
    self.assertTrue(by_bar.peys().aslist() ==
            [[['bar', 'foo'], ['bar', 'foo']], [['bar', 'foo']]])
    pl = plist['foo {}', 'bar {}', 'baz {}']
    # Basic positional argument passing:
    self.assertTrue(pl.format(0).aslist() ==
            ['foo 0', 'bar 0', 'baz 0'])
    # Passing a plist in a positional argument:
    self.assertTrue(pl.format(pl._[:3:1]).aslist() ==
            ['foo foo', 'bar bar', 'baz baz'])
    # Basic keyword argument passing:
    pl = pl.replace('{}', '{foo}')
    self.assertTrue(pl.format(foo=0).aslist() ==
            ['foo 0', 'bar 0', 'baz 0'])
    # Passing a plist as a keyword argument:
    self.assertTrue(pl.format(foo=pl._[:3:1]).aslist() ==
            ['foo foo', 'bar bar', 'baz baz'])
    pl = plist['foo {}', 'bar {}', 'baz {}']
    by = pl._[0].groupby()  # Group by first character.
    self.assertTrue(by.aslist() ==
            [['foo {}'], ['bar {}', 'baz {}']])
    # Basic positional argument passing:
    self.assertTrue(by.format(0).aslist() ==
            [['foo 0'], ['bar 0', 'baz 0']])
    # Passing a plist in a positional argument:
    self.assertTrue(by.format(by._[:3:1]).aslist() ==
            [['foo foo'], ['bar bar', 'baz baz']])
    # Basic keyword argument passing:
    by = by.replace('{}', '{foo}')
    self.assertTrue(by.format(foo=0).aslist() ==
            [['foo 0'], ['bar 0', 'baz 0']])
    # Passing a plist as a keyword argument:
    self.assertTrue(by.format(foo=by._[:3:1]).aslist() ==
            [['foo foo'], ['bar bar', 'baz baz']])


  def test_from_docs_pstar_plist___contains__(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(2 in foos.foo)
    self.assertTrue(dict(foo=0, bar=0) in foos)
    by_bar = foos.bar.groupby()
    self.assertTrue(2 in by_bar.foo)
    self.assertTrue(dict(foo=0, bar=0) in by_bar)


  def test_from_docs_pstar_plist___delattr__(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos.foo
    self.assertTrue(foos.aslist() ==
            [{'bar': 0}, {'bar': 1}, {'bar': 0}])
    # Deletion works on grouped plists as well:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    # Assignment to an existing attribute:
    del by_bar.foo
    self.assertTrue(by_bar.aslist() ==
            [[{'bar': 0}, {'bar': 0}], [{'bar': 1}]])


  def test_from_docs_pstar_plist___delitem__(self):
    # Basic scalar indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos[0]
    self.assertTrue(foos.aslist() ==
            [dict(foo=1, bar=1), dict(foo=2, bar=0)])
    # plist slice indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos[:2]
    self.assertTrue(foos.aslist() ==
            [dict(foo=2, bar=0)])
    # plist int list indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos[[0, 2]]
    self.assertTrue(foos.aslist() ==
            [dict(foo=1, bar=1)])
    # Basic scalar indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos['foo']
    self.assertTrue(foos.aslist() ==
            [dict(bar=0), dict(bar=1), dict(bar=0)])
    # tuple indexing
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos[('foo', 'bar')]
    self.assertTrue(foos.aslist() ==
            [dict(), dict(), dict()])
    # list indexing
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    del foos[['foo', 'bar', 'bar']]
    self.assertTrue(foos.aslist() ==
            [dict(bar=0), dict(foo=1), dict(foo=2)])
    # Basic scalar indexing:
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    del pl._[0]
    self.assertTrue(pl.aslist() ==
            [[2, 3], [5, 6], [8, 9]])
    # slice indexing (note the use of the 3-argument version of slicing):
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    del pl._[:2:1]
    self.assertTrue(pl.aslist() ==
            [[3], [6], [9]])


  def test_from_docs_pstar_plist___delslice__(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      pl = plist['abc', 'def', 'ghi']
      del pl[:2:1]
      self.assertTrue(pl.aslist() ==
              ['ghi'])
      # Change slices of the lists:
      pl = plist['abc', 'def', 'ghi']
      # Turn strings into mutable lists:
      pl = pl.apply(list)
      del pl._[:2:1]
      # Turn lists back into strings:
      pl = pl.apply(''.join)
      self.assertTrue(pl.aslist() ==
              ['c', 'f', 'i'])
      pl = plist['abc', 'def', 'ghi']
      # Turn strings into mutable lists:
      pl = pl.apply(list)
      del pl._[:2]
      # Turn lists back into strings:
      pl = pl.apply(''.join)
      self.assertTrue(pl.aslist() ==
              ['c', 'f', 'i'])
      # Logs:
      #   qj: <pstar> __delslice__: WARNING! <1711>: (multiline log follows)
      #   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
      #   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
      #   This avoids the broken code path in the python compiler.
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_plist___enter__(self):
    import glob, os
    path = os.path.dirname(__file__)
    filenames = plist(glob.glob(os.path.join(path, '*.py')))
    with filenames.apply(open, 'r') as f:
      texts = f.read()
    self.assertTrue(len(texts) >= 1)
    self.assertTrue(len(texts.all(isinstance, str)) >= 1)


  def test_from_docs_pstar_plist___getattribute__(self):
    pl = plist[[1, 2, 3], [4, 5, 6]]
    pl.append([7, 8, 9])
    self.assertTrue(pl.aslist() ==
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    pl.append_(10)
    self.assertTrue(pl.aslist() ==
            [[1, 2, 3, 10], [4, 5, 6, 10], [7, 8, 9, 10]])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.apply(str).aslist() ==
            ['[0, 2]', '[1]'])
    self.assertTrue(by_bar.foo.apply_(str).aslist() ==
            [['0', '2'], ['1']])
    # (Note that it is better to use `plist.pstr` to get string representation of
    # leaf elements:)
    self.assertTrue(by_bar.foo.pstr().aslist() ==
            [['0', '2'], ['1']])


  def test_from_docs_pstar_plist___getitem__(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    # Basic scalar indexing:
    self.assertTrue(foos[0] ==
            dict(foo=0, bar=0))
    # plist slice indexing:
    self.assertTrue(foos[:2].aslist() ==
            [dict(foo=0, bar=0), dict(foo=1, bar=1)])
    # plist int list indexing:
    self.assertTrue(foos[[0, 2]].aslist() ==
            [dict(foo=0, bar=0), dict(foo=2, bar=0)])
    # Basic scalar indexing:
    self.assertTrue(foos['foo'].aslist() ==
            [0, 1, 2])
    # tuple indexing
    self.assertTrue(foos[('foo', 'bar')].aslist() ==
            [(0, 0), (1, 1), (2, 0)])
    # list indexing
    self.assertTrue(foos[['foo', 'bar', 'bar']].aslist() ==
            [0, 1, 0])
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    # Basic scalar indexing:
    self.assertTrue(pl._[0].aslist() ==
            [1, 4, 7])
    # slice indexing (note the use of the 3-argument version of slicing):
    self.assertTrue(pl._[:2:1].aslist() ==
            [[1, 2], [4, 5], [7, 8]])
    # list indexing:
    pl = pl.np()
    self.assertTrue(pl._[[True, False, True]].apply(list).aslist() ==
            [[1, 3], [4, 6], [7, 9]])


  def test_from_docs_pstar_plist___getslice__(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      pl = plist['abc', 'def', 'ghi']
      self.assertTrue(pl[:2:1].aslist() ==
              ['abc', 'def'])
      self.assertTrue(pl._[:2:1].aslist() ==
              ['ab', 'de', 'gh'])
      self.assertTrue(pl._[:2].aslist() ==
              ['ab', 'de', 'gh'])
      # Logs:
      #   qj: <pstar> __getslice__: WARNING! <1711>: (multiline log follows)
      #   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
      #   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
      #   This avoids the broken code path in the python compiler.
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_plist___init__(self):
    # Empty plists:
    pl = plist()
    pl = plist([])
    # Convenience constructor for list literals:
    pl = plist[1, 2, 3]
    pl = plist[1,]  # Note the trailing comma, which is required for 1-element lists.
    # Initialization from other lists or plists:
    pl = plist(['a', 'b', 'c'])
    pl = plist(pl)
    # Initialization from iterables:
    pl = plist(range(5))
    pl = plist([i for i in range(5)])
    pl = plist((i for i in range(5)))
    # Passing root (advanced usage -- not generally necessary):
    pl = plist([1, 2, 3], root=plist(['a', 'b', 'c']))


  def test_from_docs_pstar_plist___setattr__(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    # Assignment to an existing attribute:
    foos.foo += 1
    self.assertTrue(foos.foo.aslist() ==
            [1, 2, 3])
    # Scalar assignment to a new attribute:
    foos.baz = -1
    self.assertTrue(foos.baz.aslist() ==
            [-1, -1, -1])
    # plist assignment to an attribute:
    foos.baz *= foos.foo + foos.bar
    self.assertTrue(foos.baz.aslist() ==
            [-1, -3, -3])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    # Assignment to an existing attribute:
    by_bar.foo += 1
    self.assertTrue(by_bar.foo.aslist() ==
            [[1, 3], [2]])
    # Scalar assignment to a new attribute:
    by_bar.baz = -1
    self.assertTrue(by_bar.baz.aslist() ==
            [[-1, -1], [-1]])
    # plist assignment to an attribute:
    by_bar.baz *= by_bar.foo + by_bar.bar
    self.assertTrue(by_bar.baz.aslist() ==
            [[-1, -3], [-3]])


  def test_from_docs_pstar_plist___setitem__(self):
    # Basic scalar indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos[0] = 13
    self.assertTrue(foos.aslist() ==
            [13, dict(foo=1, bar=1), dict(foo=2, bar=0)])
    # plist slice indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos[:2] = plist[12, 13]
    self.assertTrue(foos.aslist() ==
            [12, 13, dict(foo=2, bar=0)])
    # plist int list indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos[[0, 2]] = plist[12, 13]
    self.assertTrue(foos.aslist() ==
            [12, dict(foo=1, bar=1), 13])
    # Basic scalar indexing:
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos['foo'] = plist[4, 5, 6]
    self.assertTrue(foos.aslist() ==
            [dict(foo=4, bar=0), dict(foo=5, bar=1), dict(foo=6, bar=0)])
    # list indexing
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos[['foo', 'bar', 'bar']] = plist[4, 5, 6]
    self.assertTrue(foos.aslist() ==
            [dict(foo=4, bar=0), dict(foo=1, bar=5), dict(foo=2, bar=6)])
    # Basic scalar indexing:
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    pl._[0] = 13
    self.assertTrue(pl.aslist() ==
            [[13, 2, 3], [13, 5, 6], [13, 8, 9]])
    # slice indexing (note the use of the 3-argument version of slicing):
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    pl._[:2:1] = pl._[1:3:1]
    self.assertTrue(pl.aslist() ==
            [[2, 3, 3], [5, 6, 6], [8, 9, 9]])
    # list indexing:
    pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]].np()
    pl._[[True, False, True]] = plist[[5, 6], [7, 8], [9, 0]]
    self.assertTrue(pl.apply(list).aslist() ==
            [[5, 2, 6], [7, 5, 8], [9, 8, 0]])


  def test_from_docs_pstar_plist___setslice__(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      pl = plist['abc', 'def', 'ghi']
      pl[:2:1] = plist['dec', 'abf']
      self.assertTrue(pl.aslist() ==
              ['dec', 'abf', 'ghi'])
      # Turn strings into mutable lists:
      pl = pl.apply(list)
      # Change slices of the lists:
      pl._[:2:1] = pl._[1:3:1]
      # Turn the lists back into strings
      pl = pl.apply(''.join)
      self.assertTrue(pl.aslist() ==
              ['ecc', 'bff', 'hii'])
      pl = pl.apply(list)
      pl._[:2] = plist['ab', 'de', 'gh']
      pl = pl.apply(''.join)
      self.assertTrue(pl.aslist() ==
              ['abc', 'def', 'ghi'])
      # Logs:
      #   qj: <pstar> __setslice__: WARNING! <1711>: (multiline log follows)
      #   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
      #   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
      #   This avoids the broken code path in the python compiler.
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_plist_all(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.all(isinstance, pdict).aslist() ==
            [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.all(lambda x: x > 0).aslist() == [])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.all_(lambda x: x > 0).aslist() ==
            [[], [1]])
    self.assertTrue(by_bar.foo.all_(lambda x: x > 0).nonempty().root().aslist() ==
            [[{'bar': 1, 'foo': 1}]])


  def test_from_docs_pstar_plist_any(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.any(isinstance, pdict).aslist() ==
            [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.any(lambda x: x < 0).aslist() == [])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.any_(lambda x: x > 1).aslist() ==
            [[0, 2], []])
    self.assertTrue(by_bar.foo.any_(lambda x: x > 1).nonempty().root().aslist() ==
            [[{'bar': 0, 'foo': 0}, {'bar': 0, 'foo': 2}]])


  def test_from_docs_pstar_plist_apply(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.apply('foo: {}'.format).aslist() ==
            ['foo: 0', 'foo: 1', 'foo: 2'])
    self.assertTrue(foos.foo.apply('foo: {}, bar: {}'.format, foos.bar).aslist() ==
            ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])
    self.assertTrue(foos.foo.apply('foo: {}, bar: {bar}'.format, bar=foos.bar).aslist() ==
            ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])
    # The same as above, but in parallel:
    self.assertTrue(foos.foo.apply('foo: {}, bar: {}'.format, foos.bar, psplit=1).aslist() ==
            ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.apply('bar: {bar} => {}'.format, bar=foos.bar.puniq()).aslist() ==
            ['bar: 0 => [0, 2]', 'bar: 1 => [1]'])
    self.assertTrue(by_bar.foo.apply_('bar: {bar} => {}'.format, bar=by_bar.bar).aslist() ==
            [['bar: 0 => 0', 'bar: 0 => 2'], ['bar: 1 => 1']])
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6
    by_bar_baz = foos.bar.groupby().baz.groupby()
    by_bar_baz_apply_paslist = by_bar_baz.foo.apply(
        lambda x, *a, **kw: {'{x}: {a} ({kw})'.format(x=x, a=a, kw=kw)}, by_bar_baz.baz, bar=by_bar_baz.bar, paslist=True)
    by_bar_baz_apply_paslist_psplat = by_bar_baz.foo.apply(
        lambda *a, **kw: {'{a} ({kw})'.format(a=a, kw=kw)}, by_bar_baz.baz, bar=by_bar_baz.bar, paslist=True, psplat=True)
    self.assertTrue(by_bar_baz_apply_paslist.aslist() ==
            [["[[0], [2], [4]]: ([[3], [1], [2]],) ({'bar': [[0], [0], [0]]})"],
             ["[[1, 3]]: ([[6, 6]],) ({'bar': [[1, 1]]})"]])
    self.assertTrue(by_bar_baz_apply_paslist_psplat.aslist() ==
            [["([0], [2], [4], [[3], [1], [2]]) ({'bar': [[0], [0], [0]]})"],
             ["([1, 3], [[6, 6]]) ({'bar': [[1, 1]]})"]])


  def test_from_docs_pstar_plist_aslist(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.apply(type).aslist() == [plist, plist])
    self.assertTrue([type(x) for x in by_bar.aslist()] == [list, list])


  def test_from_docs_pstar_plist_aspdict(self):
    pl = plist['foo', 'bar', 'baz']
    self.assertTrue(pl.pdict() ==
            dict(foo='foo', bar='bar', baz='baz'))
    self.assertTrue(pl.replace('a', '').replace('o', '').pdict() ==
            dict(foo='f', bar='br', baz='bz'))
    foos = plist([pdict(foo=0, bar=0, baz=3), pdict(foo=1, bar=1, baz=2), pdict(foo=2, bar=0, baz=1)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.bar.ungroup().puniq().zip(by_bar).aspdict() ==
            {0: [{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 1, 'foo': 2}],
             1: [{'bar': 1, 'baz': 2, 'foo': 1}]})
    self.assertTrue([type(x) for x in by_bar.astuple()] == [tuple, tuple])


  def test_from_docs_pstar_plist_aspset(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.bar.aspset() == pset([0, 1]))
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.bar.apply(type).aslist() == [plist, plist])
    self.assertTrue(type(by_bar.bar.aspset()) == pset)
    self.assertTrue([type(x) for x in by_bar.bar.aspset()] == [frozenpset, frozenpset])


  def test_from_docs_pstar_plist_astuple(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.apply(type).aslist() == [plist, plist])
    self.assertTrue([type(x) for x in by_bar.astuple()] == [tuple, tuple])


  def test_from_docs_pstar_plist_binary_op(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    self.assertTrue((foos.foo + foos.baz).aslist() ==
            [3, 7, 7])
    self.assertTrue((2 * (foos.foo + 7)).aslist() ==
            [14, 16, 18])
    by_bar = foos.bar.groupby()
    self.assertTrue((by_bar.foo + by_bar.baz).aslist() ==
            [[3, 7], [7]])
    self.assertTrue((2 * (by_bar.foo + 7)).aslist() ==
            [[14, 18], [16]])
    self.assertTrue(('foo: ' + foos.foo.pstr() + ' bar: ' + foos.bar.pstr()).aslist() ==
            ['foo: 0 bar: 0', 'foo: 1 bar: 1', 'foo: 2 bar: 0'])
    self.assertTrue(foos.foo.apply('foo: {} bar: {}'.format, foos.bar).aslist() ==
            ['foo: 0 bar: 0', 'foo: 1 bar: 1', 'foo: 2 bar: 0'])
    self.assertTrue(('foo: ' + by_bar.foo.pstr() + ' bar: ' + by_bar.bar.pstr()).aslist() ==
            [['foo: 0 bar: 0', 'foo: 2 bar: 0'], ['foo: 1 bar: 1']])
    self.assertTrue(by_bar.foo.apply('foo: {} bar: {}'.format, by_bar.bar).aslist() ==
            ['foo: [0, 2] bar: [0, 0]', 'foo: [1] bar: [1]'])
    self.assertTrue(by_bar.foo.apply_('foo: {} bar: {}'.format, by_bar.bar).aslist() ==
            [['foo: 0 bar: 0', 'foo: 2 bar: 0'], ['foo: 1 bar: 1']])


  def test_from_docs_pstar_plist_comparator(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    zero_bars = foos.bar == 0
    self.assertTrue(zero_bars.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    nonzero_bars = foos.bar != 0
    self.assertTrue(nonzero_bars.aslist() ==
            [{'foo': 1, 'bar': 1}])
    self.assertTrue((foos == zero_bars).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    self.assertTrue((foos.foo > foos.bar).aslist() ==
            [{'foo': 2, 'bar': 0}])
    self.assertTrue((foos.foo == [0, 1, 3]).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    nonzero_by_bar_foo = by_bar_foo.bar > 0
    self.assertTrue(nonzero_by_bar_foo.aslist() ==
            [[[],
              []],
             [[{'bar': 1, 'foo': 1}]]])
    zero_by_bar_foo = by_bar_foo.foo != nonzero_by_bar_foo.foo
    self.assertTrue(zero_by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    self.assertTrue((by_bar_foo.foo == [[[0], [3]], [[1]]]).aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              []],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue((foos.foo == [0, 1, 3, 4]).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    self.assertTrue((by_bar_foo.foo == [0, 1, 3, 4]).aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              []],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue((foos.foo == []).aslist() == [])
    self.assertTrue((foos.foo < []).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue((by_bar_foo == nonzero_by_bar_foo).aslist() ==
            [[[],
              []],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue((by_bar_foo.foo > nonzero_by_bar_foo.foo).aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    self.assertTrue((by_bar_foo == nonzero_by_bar_foo).nonempty(-1).aslist() ==
            [[[{'foo': 1, 'bar': 1}]]])


  def test_from_docs_pstar_plist_copy(self):
    pl1 = plist[1, 2, 3]
    pl2 = pl1.copy()
    self.assertTrue(pl1 is not pl2)
    self.assertTrue(pl1.root() is pl1 and pl2.root() is pl2)
    pl3 = pl2 + 1
    pl4 = pl3.copy()
    self.assertTrue(pl4.root().aslist() == pl3.root().aslist())
    self.assertTrue(pl4.root() is not pl3.root())
    self.assertTrue(pl4.root().aslist() == pl2.aslist())
    self.assertTrue(pl4.root() is not pl2)


  def test_from_docs_pstar_plist_enum(self):
    pl = plist['a', 'b', 'c']
    self.assertTrue(pl.enum().aslist() ==
            [(0, 'a'), (1, 'b'), (2, 'c')])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.enum_().aslist() ==
            [[(0, 0), (1, 2)], [(0, 1)]])


  def test_from_docs_pstar_plist_filter(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.filter().aslist() ==
            [dict(foo=1, bar=1), dict(foo=2, bar=0)])
    self.assertTrue(foos.foo.filter(lambda x: x < 2).aslist() ==
            [dict(foo=0, bar=0), dict(foo=1, bar=1)])
    (foos.bar == 0).bin = 'zero'
    (foos.bar == 1).bin = 1
    self.assertTrue(foos.bin.filter(isinstance, str).aslist() ==
            [{'bar': 0, 'bin': 'zero', 'foo': 0}, {'bar': 0, 'bin': 'zero', 'foo': 2}])


  def test_from_docs_pstar_plist_groupby(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    foo_by_bar = foos.bar.groupby()
    self.assertTrue(foo_by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    foos = plist([{'bar': [1, 2, 3]}, {'bar': [1, 2, 3]}])
    try:
      by_bar_crash = foos.bar.groupby()  # CRASHES!
    except Exception as e:
      self.assertTrue(isinstance(e, TypeError))
    by_bar_pstr = foos.bar.pstr().groupby()
    self.assertTrue(by_bar_pstr.aslist() ==
            [[{'bar': [1, 2, 3]},
              {'bar': [1, 2, 3]}]])
    by_bar_id = foos.bar.apply(id).groupby()
    self.assertTrue(by_bar_id.aslist() ==
            [[{'bar': [1, 2, 3]}],
             [{'bar': [1, 2, 3]}]])


  def test_from_docs_pstar_plist_lfill(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.lfill() ==
            [0, 1, 2])
    self.assertTrue(foos.lfill(-7) ==
            [-7, -6, -5])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.lfill() ==
            [[[0], [1]], [[2]]])
    self.assertTrue(by_bar_foo.lfill_() ==
            [[[0], [1]], [[0]]])
    self.assertTrue(by_bar_foo.lfill(pepth=2) ==
            [[[0], [0]], [[0]]])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    self.assertTrue(filtered.lfill(3) ==
            [[[3], [4]], [[]]])


  def test_from_docs_pstar_plist_logical_op(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    self.assertTrue(((foos.bar == 0) & (foos.baz == 3)).aslist() ==
            [{'baz': 3, 'foo': 0, 'bar': 0}])
    self.assertTrue(((foos.bar == 0) | (foos.baz == 3)).aslist() ==
            [{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}])
    self.assertTrue(((foos.bar == 0) ^ (foos.baz == 3)).aslist() ==
            [{'bar': 0, 'baz': 5, 'foo': 2}])
    by_bar = foos.bar.groupby()
    self.assertTrue(((by_bar.bar == 0) & (by_bar.bar == 1)).aslist() ==
            [[], []])
    self.assertTrue(((by_bar.bar == 0) & (by_bar.bar <= 1)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}], []])
    self.assertTrue(((by_bar.baz == 3) | (by_bar.baz == 6)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
    self.assertTrue(((by_bar.baz == 6) | (by_bar.baz <= 4)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
    self.assertTrue(((by_bar.baz == 3) ^ (by_bar.baz == 6)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
    self.assertTrue(((by_bar.baz == 6) ^ (by_bar.bar <= 4)).aslist() ==
            [[{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}], []])
    self.assertTrue((foos.baz & 1).aslist() ==
            [1, 0, 1])
    self.assertTrue((by_bar.baz | 1).aslist() ==
            [[3, 5], [7]])
    self.assertTrue((1 ^ by_bar.baz).aslist() ==
            [[2, 4], [7]])


  def test_from_docs_pstar_plist_me(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    foos.baz = 3 * foos.foo + foos.bar
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0, 'baz': 0},
             {'foo': 1, 'bar': 1, 'baz': 4},
             {'foo': 2, 'bar': 0, 'baz': 6}])
    def new_context():
      me = plist()
      foos.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.bar)
    new_context()
    def new_context():
      baz = plist()
      foos.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
    new_context()
    def new_context():
      me2 = plist()
      foos.bar.groupby().baz.sortby_().groupby().me(me2).foo.plt().plot(me2.foo + 1)
    new_context()
    def new_context():
      foos.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.baz)
      foos.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
      del globals()['me']
      del globals()['baz']
    new_context()


  def test_from_docs_pstar_plist_none(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.none(isinstance, pset).aslist() ==
            [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.none(lambda x: x > 1).aslist() == [])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.none_(lambda x: x > 1).aslist() ==
            [[], [1]])
    self.assertTrue(by_bar.foo.none_(lambda x: x > 1).nonempty().root().aslist() ==
            [[{'bar': 1, 'foo': 1}]])


  def test_from_docs_pstar_plist_nonempty(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    foo_by_bar = foos.bar.groupby()
    self.assertTrue(foo_by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    filtered = foo_by_bar.foo != 1
    self.assertTrue(filtered.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             []])
    filtered_nonempty = filtered.nonempty()
    self.assertTrue(filtered_nonempty.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}]])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    filtered = by_bar_foo.foo != 1
    self.assertTrue(filtered.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    filtered_nonempty_0 = filtered.nonempty()
    self.assertTrue(filtered_nonempty_0.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[]]])
    filtered_nonempty_1 = filtered.nonempty(1)
    self.assertTrue(filtered_nonempty_1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]]])
    filtered_nonempty_n1 = filtered.nonempty(-1)
    self.assertTrue(filtered_nonempty_n1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]]])
    filtered_nonempty_p1 = filtered.nonempty(pepth=1)
    self.assertTrue(filtered_nonempty_p1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             []])
    filtered_nonempty_u1 = filtered.nonempty_()
    self.assertTrue(filtered_nonempty_u1.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             []])


  def test_from_docs_pstar_plist_np(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1
    self.assertTrue(foos.aslist() ==
            [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
             {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 1},
             {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
             {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 3},
             {'bar': 0, 'baz': 7, 'bin': -1, 'foo': 4}])
    self.assertTrue(foos.foo.wrap().np().sum().aslist() ==
            [10])
    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz
    # Filters for the max per group, which includes the two-way tie in the first group.
    (baz == baz.np().max()).bin = 13
    self.assertTrue(by_bar.aslist() ==
            [[{'bar': 1, 'baz': 6, 'bin': 13, 'foo': 1},
              {'bar': 1, 'baz': 6, 'bin': 13, 'foo': 3}],
             [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
              {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
              {'bar': 0, 'baz': 7, 'bin': 13, 'foo': 4}]])
    self.assertTrue((by_bar.foo.np() * by_bar.baz.np() - by_bar.bin.np()).sum().aslist() ==
            [-2, 27])


  def test_from_docs_pstar_plist_pand(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      foos.baz = 3 * foos.foo + foos.bar
      self.assertTrue(foos.aslist() ==
              [{'foo': 0, 'bar': 0, 'baz': 0},
               {'foo': 1, 'bar': 1, 'baz': 4},
               {'foo': 2, 'bar': 0, 'baz': 6}])
      def new_context():
        self.assertTrue(foos.bar.groupby().baz.groupby().foo.pand().root().bar.pand().ungroup()
                    .apply_(qj, '(foo, bar)') ==
                [[[(0, 0)],
                  [(2, 0)]],
                 [[(1, 1)]]])
      new_context()
      # Logs:
      #   qj: <pstar> apply: (foo, bar) <1249>: (0, 0)
      #   qj: <pstar> apply: (foo, bar) <1249>: (2, 0)
      #   qj: <pstar> apply: (foo, bar) <1249>: (1, 1)
      def new_context():
        (foos.bar.groupby().baz.groupby().foo.pand().root().bar.pstr().pand()
             .ungroup().apply_(qj, psplat=True, b=0))
      new_context()
      # Logs:
      #   qj: <pstar> apply: (foo, bar) <2876>: (0, 0)
      #   qj: <pstar> apply: (foo, bar) <2876>: (2, 0)
      #   qj: <pstar> apply: (foo, bar) <2876>: (1, 1)
      #   qj: <pstar> apply: (0, 0) <2876>: (0, 0)
      #   qj: <pstar> apply: (2, 0) <2876>: (2, 0)
      #   qj: <pstar> apply: (1, 1) <2876>: (1, 1)
      def new_context():
        me = plist()
        self.assertTrue(foos.bar.groupby().baz.groupby().me().foo.pand().root().bar.pand().ungroup()
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
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_plist_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1
    self.assertTrue(foos.aslist() ==
            [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
             {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 1},
             {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
             {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 3},
             {'bar': 0, 'baz': 7, 'bin': -1, 'foo': 4}])
    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz
    (baz == baz.np().max()).bin = 13
    self.assertTrue(by_bar.aslist() ==
            [[{'bar': 1, 'baz': 6, 'bin': 13, 'foo': 1},
              {'bar': 1, 'baz': 6, 'bin': 13, 'foo': 3}],
             [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
              {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
              {'bar': 0, 'baz': 7, 'bin': 13, 'foo': 4}]])
    self.assertTrue(str(foos.pd()) ==
            '   bar  baz  bin  foo\n'
            '0    1    6   13    1\n'
            '1    1    6   13    3\n'
            '2    0    3   -1    0\n'
            '3    0    5   -1    2\n'
            '4    0    7   13    4')
    self.assertTrue(str(foos.pd(index='foo')) ==
            '     bar  baz  bin\n'
            'foo               \n'
            '1      1    6   13\n'
            '3      1    6   13\n'
            '0      0    3   -1\n'
            '2      0    5   -1\n'
            '4      0    7   13')
    self.assertTrue(by_bar.pd_().pstr().aslist() ==
            ['   bar  baz  bin  foo\n'
             '0    1    6   13    1\n'
             '1    1    6   13    3',
             '   bar  baz  bin  foo\n'
             '0    0    3   -1    0\n'
             '1    0    5   -1    2\n'
             '2    0    7   13    4'])


  def test_from_docs_pstar_plist_pdepth(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.pdepth().aslist() ==
            [0])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.pdepth().aslist() ==
            [[[2], [2]], [[2]]])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    self.assertTrue(filtered.pdepth().aslist() ==
            [[[2], [2]], [[]]])
    self.assertTrue(foos.pdepth(s=1) == 0)
    self.assertTrue(by_bar_foo.pdepth(1) == 2)
    self.assertTrue(filtered.pdepth(True) == 2)


  def test_from_docs_pstar_plist_pdict(self):
    pl = plist['foo', 'bar', 'baz']
    self.assertTrue(pl.pdict() ==
            dict(foo='foo', bar='bar', baz='baz'))
    self.assertTrue(pl.replace('a', '').replace('o', '').pdict() ==
            dict(foo='f', bar='br', baz='bz'))
    pd = pdict(foo=1, bar=2, floo=0)
    self.assertTrue(pd.pitems().pdict() == pd)
    self.assertTrue(pd.palues().pdict() == pd)
    self.assertTrue((pd.palues() + 2).pdict() ==
            dict(foo=3, bar=4, floo=2))
    self.assertTrue(pd.peys()._[0].pdict(),
            pdict(foo='f', bar='b', floo='f'))
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.pstr().zip(foos.bar).uproot().pdict() ==
            {'0': 0, '1': 1, '2': 0})
    self.assertTrue(plist[('foo', 1), ('foo', 2)].pdict() ==
            dict(foo=2))


  def test_from_docs_pstar_plist_pequal(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.pequal(foos) == True)
    zero_bars = foos.bar == 0
    self.assertTrue(zero_bars.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    self.assertTrue((foos == zero_bars).aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.pequal(zero_bars) == False)


  def test_from_docs_pstar_plist_pfill(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.pfill().aslist() ==
            [0, 1, 2])
    self.assertTrue(foos.pfill(-7).aslist() ==
            [-7, -6, -5])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.pfill().aslist() ==
            [[[0], [1]], [[2]]])
    self.assertTrue(by_bar_foo.pfill_().aslist() ==
            [[[0], [1]], [[0]]])
    self.assertTrue(by_bar_foo.pfill(pepth=2).aslist() ==
            [[[0], [0]], [[0]]])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    self.assertTrue(filtered.pfill(3).aslist() ==
            [[[3], [4]], [[]]])


  def test_from_docs_pstar_plist_pleft(self):
    with mock.patch('matplotlib.pyplot.show'):
      foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      self.assertTrue(foos.aslist() ==
              [{'foo': 0, 'bar': 0},
               {'foo': 1, 'bar': 1},
               {'foo': 2, 'bar': 0}])
      self.assertTrue(foos.pleft().aslist() ==
              [2, 1, 0])
      by_bar_foo = foos.bar.groupby().foo.groupby()
      self.assertTrue(by_bar_foo.aslist() ==
              [[[{'foo': 0, 'bar': 0}],
                [{'foo': 2, 'bar': 0}]],
               [[{'foo': 1, 'bar': 1}]]])
      self.assertTrue(by_bar_foo.pleft().aslist() ==
              [[[2], [1]], [[0]]])
      self.assertTrue(by_bar_foo.pleft_().aslist() ==
              [[[1], [0]], [[0]]])
      self.assertTrue(by_bar_foo.pleft(pepth=2).aslist() ==
              [[[0], [0]], [[0]]])
      filtered = by_bar_foo.bar == 0
      self.assertTrue(filtered.aslist() ==
              [[[{'bar': 0, 'foo': 0}],
                [{'bar': 0, 'foo': 2}]],
               [[]]])
      self.assertTrue(filtered.pleft().aslist() ==
              [[[1], [0]], [[]]])
      def plot(x, remaining):
        plt.plot(x)
        if remaining == 0:
          plt.show()
      (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
      (foos.bar == 1).baz = 6
      foos.bin = (foos.baz + foos.bar) * foos.foo
      by_bar_baz_bin = foos.bar.groupby().baz.groupby().bin.groupby()
      by_bar_baz_bin.foo.apply(plot, by_bar_baz_bin.pleft(pepth=2), pepth=2)


  def test_from_docs_pstar_plist_plen(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.plen().aslist() ==
            [3])
    self.assertTrue(foos.plen(1).aslist() ==
            [3])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.plen().aslist() ==
            [2])
    self.assertTrue(by_bar_foo.plen(r=1).aslist() ==
            [[3]])
    self.assertTrue(by_bar_foo.plen(2).aslist() ==
            [[[3]]])
    self.assertTrue(by_bar_foo.plen(-1).aslist() ==
            [[[3]]])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    self.assertTrue(filtered.plen().aslist() ==
            [2])
    self.assertTrue(filtered.plen(-1).aslist() ==
            [[[2]]])
    self.assertTrue(foos.plen(s=1) == 3)
    self.assertTrue(by_bar_foo.plen(r=2, s=1) == 3)
    self.assertTrue(filtered.plen(-1, s=True) == 2)


  def test_from_docs_pstar_plist_plt(self):
    with mock.patch('matplotlib.pyplot.show'):
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


  def test_from_docs_pstar_plist_pset(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.pitems().pset().aslist() ==
            [{('foo', 0), ('bar', 0)}, {('foo', 1), ('bar', 1)}, {('foo', 2), ('bar', 0)}])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.pset().aslist() ==
            [{0, 2}, {1}])


  def test_from_docs_pstar_plist_pshape(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.pshape().aslist() ==
            [3])
    foo_by_bar = foos.bar.groupby()
    self.assertTrue(foo_by_bar.aslist() ==
            [[{'bar': 0, 'foo': 0},
              {'bar': 0, 'foo': 2}],
             [{'bar': 1, 'foo': 1}]])
    self.assertTrue(foo_by_bar.pshape().aslist() ==
            [[2], [1]])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.pshape().aslist() ==
            [[[1], [1]], [[1]]])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    self.assertTrue(filtered.pshape().aslist() ==
            [[[1], [1]], [[]]])


  def test_from_docs_pstar_plist_pstr(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.foo.pstr().aslist() ==
            ['0', '1', '2'])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.foo.pstr().aslist() ==
            [['0', '2'], ['1']])
    self.assertTrue(('foo: ' + by_bar.foo.pstr() + ', bar: ' + by_bar.bar.pstr()).aslist() ==
            [['foo: 0, bar: 0', 'foo: 2, bar: 0'], ['foo: 1, bar: 1']])
    self.assertTrue(by_bar.foo.apply(str).aslist() ==
            ['[0, 2]', '[1]'])


  def test_from_docs_pstar_plist_pstructure(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.pstructure().aslist() ==
            [3])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.pstructure().aslist() ==
            [2, 3, 3])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    self.assertTrue(filtered.pstructure().aslist() ==
            [2, 3, 2])


  def test_from_docs_pstar_plist_puniq(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    reduced = foos.bar.puniq()
    self.assertTrue(reduced.aslist() ==
            [0, 1])
    self.assertTrue(reduced.root().aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    foo_by_bar = foos.bar.groupby()
    self.assertTrue(foo_by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    reduced = foo_by_bar.bar.puniq()
    self.assertTrue(reduced.aslist() ==
            [[0], [1]])
    self.assertTrue(reduced.root().aslist() ==
            [[{'foo': 0, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    reduced_no_effect = by_bar_foo.bar.puniq()
    self.assertTrue(reduced_no_effect.aslist() ==
            [[[0], [0]], [[1]]])
    self.assertTrue(reduced_no_effect.root().aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=0, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 0, 'bar': 0}])
    try:
      reduced_crash = foos.puniq()  # CRASHES!
    except Exception as e:
      self.assertTrue(isinstance(e, TypeError))
    reduced_pstr = foos.pstr().puniq()
    self.assertTrue(reduced_pstr.aslist() ==
            ["{'bar': 0, 'foo': 0}",
             "{'bar': 1, 'foo': 1}"])
    self.assertTrue(reduced_pstr.root().aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    reduced_id = foos.apply(id).puniq()
    self.assertTrue(reduced_id.root().aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 0, 'bar': 0}])


  def test_from_docs_pstar_plist_qj(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
      self.assertTrue(foos.foo.qj('foo').aslist() ==
              [0, 1, 2])
      # Logs:
      # qj: <calling_module> calling_func: foo <3869>: [0, 1, 2]
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_plist_reduce(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      s = 'foo bar was a baz of bin'
      pl = plist['foo', 'bar', 'baz', 'bin']
      reduced = pl.reduce(lambda s, x, y: qj(s).replace(x, y), s, pl._[::-1])
      # Logs:
      #   qj: <pstar> reduce: s <3451>: foo bar was a baz of bin
      #   qj: <pstar> reduce: s <3451>: oof bar was a baz of bin
      #   qj: <pstar> reduce: s <3451>: oof rab was a baz of bin
      #   qj: <pstar> reduce: s <3451>: oof rab was a zab of bin
      self.assertTrue(reduced.aslist() ==
              ['oof rab was a zab of nib'])
      self.assertTrue(reduced.root().aslist() ==
              ['foo bar was a baz of bin'])
      self.assertTrue(reduced.root().root() is pl)
      reduced = pl.reduce(lambda s, x, y: qj(s).replace(x, y), pl._[::-1], initial_value=s)
      self.assertTrue(reduced.aslist() ==
              ['oof rab was a zab of nib'])
      self.assertTrue(reduced.root().aslist() ==
              ['foo bar was a baz of bin'])
      self.assertTrue(reduced.root().root() is pl)
      pl = plist[1, 2, 3, 4, 5]
      reduced = pl.reduce(lambda x, y, z: (x + y) * z, z=pl[::-1])
      self.assertTrue(reduced.aslist() ==
              [466])
      self.assertTrue((((((1 + 2) * 5 + 3) * 4 + 4) * 3 + 5) * 2) ==
              466)
      foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0), pdict(foo=3, bar=1), pdict(foo=4, bar=0)])
      (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
      (foos.bar == 1).baz = 6
      foos.bin = (foos.baz + foos.bar) * foos.foo
      by_bar_baz_bin = foos.bar.groupby().baz.groupby().bin.groupby()
      self.assertTrue(by_bar_baz_bin.aslist() ==
              [[[[{'bar': 0, 'baz': 3, 'bin': 0, 'foo': 0}]],
                [[{'bar': 0, 'baz': 5, 'bin': 10, 'foo': 2}]],
                [[{'bar': 0, 'baz': 7, 'bin': 28, 'foo': 4}]]],
               [[[{'bar': 1, 'baz': 6, 'bin': 7, 'foo': 1}],
                 [{'bar': 1, 'baz': 6, 'bin': 21, 'foo': 3}]]]])
      import operator as op
      self.assertTrue(by_bar_baz_bin.foo.reduce(op.add, initial_value=0).aslist() ==
              [10])
      self.assertTrue(by_bar_baz_bin.foo.reduce_(op.add, initial_value=0).aslist() ==
              [[6], [4]])
      self.assertTrue(by_bar_baz_bin.foo.reduce__(op.add, initial_value=0).aslist() ==
              [[[0], [2], [4]], [[4]]])
      self.assertTrue(by_bar_baz_bin.foo.reduce___(op.add, initial_value=0).aslist() ==
              [[[[0]], [[2]], [[4]]], [[[1], [3]]]])
      self.assertTrue(by_bar_baz_bin.foo.reduce_(op.add, 0).reduce(op.mul, 1).aslist() ==
              [24])
      self.assertTrue(by_bar_baz_bin.foo.reduce([op.mul, op.add], 0).aslist() ==
              [24])
      self.assertTrue(by_bar_baz_bin.foo.reduce(op.add, by_bar_baz_bin.baz).aslist() ==
              [37])
      self.assertTrue(by_bar_baz_bin.foo.reduce([op.mul, op.add, op.mul, op.add], initial_value=by_bar_baz_bin.baz).aslist() ==
              [1323])
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_plist_remix(self):
    foos = plist([{'foo': 0, 'bar': {'baz': 13, 'bam': 0, 'bin': 'not'}},
                  {'foo': 1, 'bar': {'baz': 42, 'bam': 1, 'bin': 'good'}},
                  {'foo': 2, 'bar': {'baz': -9, 'bam': 0, 'bin': 'data'}}])
    rmx = foos.remix('foo', baz=foos.bar.baz)
    self.assertTrue(rmx.aslist() ==
            [{'foo': 0, 'baz': 13},
             {'foo': 1, 'baz': 42},
             {'foo': 2, 'baz': -9}])
    foo_by_bam = foos.bar.bam.groupby()
    self.assertTrue(foo_by_bam.aslist() ==
            [[{'foo': 0, 'bar': {'bam': 0, 'baz': 13, 'bin': 'not'}},
              {'foo': 2, 'bar': {'bam': 0, 'baz': -9, 'bin': 'data'}}],
             [{'foo': 1, 'bar': {'bam': 1, 'baz': 42, 'bin': 'good'}}]])
    rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz)
    self.assertTrue(rmx_by_bam.aslist() ==
            [{'foo': [0, 2], 'baz': [13, -9]},
             {'foo': [1],    'baz': [42]}])
    df = rmx_by_bam.pd()
    self.assertTrue(str(df) ==
            '        baz     foo\n'
            '0  [13, -9]  [0, 2]\n'
            '1      [42]     [1]')
    rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz, pepth=-1)
    self.assertTrue(rmx_by_bam.aslist() ==
            [[{'foo': 0, 'baz': 13},
              {'foo': 2, 'baz': -9}],
             [{'foo': 1, 'baz': 42}]])


  def test_from_docs_pstar_plist_root(self):
    pl = plist([1, 2, 3])
    self.assertTrue(pl.root() is pl)
    pl2 = pl + 3
    self.assertTrue(pl2.aslist() ==
            [4, 5, 6])
    self.assertTrue(pl2.root() is pl)
    self.assertTrue(pl2.pstr().root() is pl)
    self.assertTrue(pl2[0:2].aslist() ==
            [4, 5])
    self.assertTrue(pl2[0:2].root().aslist() ==
            [1, 2])
    self.assertTrue(pl2.sortby(reverse=True).aslist() ==
            [6, 5, 4])
    self.assertTrue(pl2.sortby(reverse=True).root().aslist() ==
            [3, 2, 1])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    filtered = foos.bar == 0
    self.assertTrue(filtered.aslist() ==
            [dict(foo=0, bar=0), dict(foo=2, bar=0)])
    self.assertTrue(filtered.root() is filtered)
    (foos.bar == 0).baz = 6
    (foos.bar == 1).baz = foos.foo * 2
    self.assertTrue(foos.aslist() ==
            [dict(foo=0, bar=0, baz=6), dict(foo=1, bar=1, baz=2), dict(foo=2, bar=0, baz=6)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.aslist() ==
            [[{'bar': 0, 'baz': 6, 'foo': 0}, {'bar': 0, 'baz': 6, 'foo': 2}],
             [{'bar': 1, 'baz': [0, 2, 4], 'foo': 1}]])
    self.assertTrue(by_bar.aslist() == by_bar.root().aslist())


  def test_from_docs_pstar_plist_sortby(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    bar_sorted = foos.bar.sortby()
    self.assertTrue(bar_sorted.aslist() ==
            [0, 0, 1])
    foos_sorted_by_bar = bar_sorted.root()
    self.assertTrue(foos_sorted_by_bar.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 2, 'bar': 0},
             {'foo': 1, 'bar': 1}])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.aslist() ==
            [[{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}],
             [{'foo': 1, 'bar': 1}]])
    by_bar_sorted = by_bar.bar.sortby(reverse=True)
    self.assertTrue(by_bar_sorted.aslist() ==
            [[1], [0, 0]])
    by_bar_sorted = by_bar_sorted.root()
    self.assertTrue(by_bar_sorted.aslist() ==
            [[{'foo': 1, 'bar': 1}],
             [{'foo': 0, 'bar': 0},
              {'foo': 2, 'bar': 0}]])


  def test_from_docs_pstar_plist_unary_op(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    self.assertTrue((-foos.foo).aslist() ==
            [0, -1, -2])
    self.assertTrue((~foos.foo).aslist() ==
            [-1, -2, -3])
    by_bar = foos.bar.groupby()
    self.assertTrue((-by_bar.foo).aslist() ==
            [[0, -2], [-1]])
    self.assertTrue((~by_bar.foo).aslist() ==
            [[-1, -3], [-2]])


  def test_from_docs_pstar_plist_ungroup(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.sortby().groupby()
    self.assertTrue(by_bar.ungroup().aslist() ==
            foos.aslist())
    by_bar[0].baz = 6
    by_bar[1].baz = by_bar[1].foo * 2
    by_bar_baz = by_bar.baz.groupby()
    self.assertTrue(by_bar_baz.ungroup().aslist() ==
            by_bar.aslist())
    self.assertTrue(by_bar_baz.ungroup(2).aslist() ==
            foos.aslist())
    self.assertTrue(by_bar_baz.ungroup(-1).aslist() ==
            by_bar.ungroup(-1).aslist())


  def test_from_docs_pstar_plist_uproot(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    (foos.bar == 0).baz = 6
    (foos.bar == 1).baz = foos.foo * 2
    floos = foos.rekey(dict(foo='floo'))
    self.assertTrue(floos.root() is foos)
    self.assertTrue(floos.peys()[0].aslist() ==
            ['bar', 'baz', 'floo'])
    self.assertTrue((floos.floo < 2).aslist() ==
            [dict(foo=0, bar=0, baz=6), dict(foo=1, bar=1, baz=2)])
    floos = floos.uproot()
    self.assertTrue((floos.floo < 2).aslist() ==
            [dict(floo=0, bar=0, baz=6), dict(floo=1, bar=1, baz=2)])


  def test_from_docs_pstar_plist_values_like(self):
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    self.assertTrue(foos.aslist() ==
            [{'foo': 0, 'bar': 0},
             {'foo': 1, 'bar': 1},
             {'foo': 2, 'bar': 0}])
    self.assertTrue(foos.values_like(1).aslist() ==
            [1, 1, 1])
    by_bar_foo = foos.bar.groupby().foo.groupby()
    self.assertTrue(by_bar_foo.aslist() ==
            [[[{'foo': 0, 'bar': 0}],
              [{'foo': 2, 'bar': 0}]],
             [[{'foo': 1, 'bar': 1}]]])
    self.assertTrue(by_bar_foo.values_like('foo').aslist() ==
            [[['foo'], ['foo']], [['foo']]])
    all_the_same_dict = by_bar_foo.values_like({}, pepth=2)
    self.assertTrue(all_the_same_dict.aslist() ==
            [[[{}], [{}]], [[{}]]])
    all_the_same_dict.ungroup(-1)[0].update(foo=1)
    self.assertTrue(all_the_same_dict.aslist() ==
            [[[{'foo': 1}], [{'foo': 1}]], [[{'foo': 1}]]])
    filtered = by_bar_foo.bar == 0
    self.assertTrue(filtered.aslist() ==
            [[[{'bar': 0, 'foo': 0}],
              [{'bar': 0, 'foo': 2}]],
             [[]]])
    tuples = filtered.values_like((1, 2, 3))
    self.assertTrue(tuples.aslist() ==
            [[[(1, 2, 3)], [(1, 2, 3)]], [[]]])
    all_the_same_dict = [{}] * 3
    self.assertTrue(all_the_same_dict ==
            [{}, {}, {}])
    all_the_same_dict[0].update(foo=1)
    self.assertTrue(all_the_same_dict ==
            [{'foo': 1}, {'foo': 1}, {'foo': 1}])


  def test_from_docs_pstar_plist_wrap(self):
    foos = plist([{'bar': [1, 2, 3]}, {'bar': [4, 5, 6]}])
    self.assertTrue(foos.aslist() ==
            [{'bar': [1, 2, 3]},
             {'bar': [4, 5, 6]}])
    arr1 = np.array(foos.bar.pstr().groupby().bar)
    self.assertTrue(np.all(arr1 ==
                   np.array([[[1, 2, 3]],
                             [[4, 5, 6]]])))
    arr2 = foos.bar.pstr().groupby().bar.np()
    self.assertTrue(np.all(np.array(arr2.aslist()) ==
                   np.array([np.array([[1, 2, 3]]),
                             np.array([[4, 5, 6]])])))
    arr3 = foos.bar.pstr().groupby().bar.wrap().np()
    self.assertTrue(np.all(np.array(arr3.aslist()) ==
                   np.array([np.array([[[1, 2, 3]],
                                      [[4, 5, 6]]])])))
    self.assertTrue(np.any(arr1 != arr2[0]))
    self.assertTrue(np.all(arr1 == arr3[0]))


  def test_from_docs_pstar_plist_zip(self):
    pl1 = plist['a', 'b', 'c']
    pl2 = plist[1, 2, 3]
    pl3 = plist['nother', 'ig', 'odebase']
    self.assertTrue(pl2.zip(pl1, pl3).aslist() ==
            [(1, 'a', 'nother'), (2, 'b', 'ig'), (3, 'c', 'odebase')])
    foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
    by_bar = foos.bar.groupby()
    self.assertTrue(by_bar.bar.zip(by_bar.foo).aslist() ==
            [[(0, 0), (0, 2)], [(1, 1)]])


  def test_from_docs_pstar_pset(self):
    ps = pset([1, 2.0, 'three'])
    ps = pset({1, 2.0, 'three'})
    ps = pset[1, 2.0, 'three']
    s1 = set([1, 2.0, 'three'])
    ps = pset * s1
    self.assertTrue(type(s1) == set)
    self.assertTrue(type(ps) == pset)
    self.assertTrue(ps == s1)
    s2 = ps / pset
    self.assertTrue(type(s2) == set)
    self.assertTrue(s2 == s1)


  def test_from_docs_pstar_pset_qj(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      ps = pset([1, 2.0, 'three'])
      ps.qj('ps')
      # Logs:
      # qj: <calling_module> calling_function: ps <2910>: pset({1, 2.0, 'three'})
    qj.LOG_FN = log_fn
    qj.COLOR = True


  def test_from_docs_pstar_pstar(self):
    data = [dict(foo=[0, 1, 2], bar=dict(bin=0), baz=defaultdict(int, a=1, b=2, c=3)),
            dict(foo=[1, 2, 3], bar=dict(bin=1), baz=frozenset([3, 4, 5])),
            dict(foo=[2, 3, 4], bar=dict(bin=0), baz=set([7, 8, 9]))]
    # Recursively convert all pstar-compatible types:
    pl = pstar(data)
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [plist, plist, plist])
    self.assertTrue(pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultpdict, frozenpset, pset])
    # An alternative way to do the same conversion:
    pl = pstar * data
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [plist, plist, plist])
    self.assertTrue(pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultpdict, frozenpset, pset])
    # Only convert the outermost object:
    pl = pstar + data
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.foo.apply(type).aslist() == [list, list, list])
    self.assertTrue(pl.bar.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])
    # The same outer conversion, as a function call:
    pl = pstar(data, depth=1)
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.foo.apply(type).aslist() == [list, list, list])
    self.assertTrue(pl.bar.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])
    # Convert two layers:
    pl = pstar(data, depth=2)
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [list, list, list])
    self.assertTrue(pl.bar.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])
    pl = pstar * data
    # Convert from pstar types back to python types:
    data2 = pl / pstar
    self.assertTrue(data2 == data)
    self.assertTrue(type(data2) == list)
    self.assertTrue([type(x) for x in data2] == [dict, dict, dict])
    self.assertTrue([type(x['foo']) for x in data2] == [list, list, list])
    self.assertTrue([type(x['bar']) for x in data2] == [dict, dict, dict])
    self.assertTrue([type(x['baz']) for x in data2] == [defaultdict, frozenset, set])
    # Only convert the outermost object:
    data2 = pl - pstar
    self.assertTrue(data2 == data)
    self.assertTrue(type(data2) == list)
    self.assertTrue([type(x) for x in data2] == [pdict, pdict, pdict])
    self.assertTrue([type(x['foo']) for x in data2] == [plist, plist, plist])
    self.assertTrue([type(x['bar']) for x in data2] == [pdict, pdict, pdict])
    self.assertTrue([type(x['baz']) for x in data2] == [defaultpdict, frozenpset, pset])
    d1 = {'foo': 1, 'bar': 2}
    pd = pdict * d1
    self.assertTrue(type(d1) == dict)
    self.assertTrue(type(pd) == pdict)
    self.assertTrue(pd == d1)
    d2 = pd / pdict
    self.assertTrue(type(d2) == dict)
    self.assertTrue(d2 == d1)
    pl = plist * data
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.foo.apply(type).aslist() == [plist, plist, plist])
    self.assertTrue(pl.bar.apply(type).aslist() == [dict, dict, dict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])
    data2 = data * pdict
    self.assertTrue(type(data2) == list)
    self.assertTrue(plist(data2).apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(plist(data2).foo.apply(type).aslist() == [list, list, list])
    self.assertTrue(plist(data2).bar.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(plist(data2).baz.apply(type).aslist() == [defaultdict, frozenset, set])
    pl = plist + data * pdict
    self.assertTrue(type(pl) == plist)
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [list, list, list])
    self.assertTrue(pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])
    try:
      plist * pdict * data
    except Exception as e:
      self.assertTrue(isinstance(e, ValueError))
    pl = plist + pdict * data
    self.assertTrue(type(pl) == plist)
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [list, list, list])
    self.assertTrue(pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
    pl = plist * (pdict * data)
    self.assertTrue(type(pl) == plist)
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [plist, plist, plist])
    self.assertTrue(pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
    pl = pstar * data / pset
    self.assertTrue(isinstance(pl, plist))
    self.assertTrue(pl.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.foo.apply(type).aslist() == [plist, plist, plist])
    self.assertTrue(pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
    self.assertTrue(pl.baz.apply(type).aslist() == [defaultpdict, frozenpset, set])
    # Starting from a nested pstar object, you may want to convert pdicts to dicts.
    pd = pdict(foo=plist[1, 2, 3], bar=pset[4, 5, 6], baz=pdict(a=7, b=8, d=9))
    # Subtracting by pdict will convert a top-level pdict to dict, but will leave other objects alone.
    d = pd - pdict
    self.assertTrue(type(d) == dict)
    self.assertTrue(type(d['foo']) == plist)
    self.assertTrue(type(d['bar']) == pset)
    self.assertTrue(type(d['baz']) == pdict)  # Note that the child is still a pdict!
    pl = pd.foo - pdict
    self.assertTrue(type(pl) == plist)  # The type is unchanged, since pd.foo is not a pdict
    self.assertTrue(pl is not pd.foo)  # Conversion still creates a new copy, though!
    self.assertTrue(pl == pd.foo)  # But the contents are identical, of course.
    # Dividing by pdict will convert any pdict values to dicts, but leave others unchanged.
    d = pd / pdict
    self.assertTrue(type(d) == dict)
    self.assertTrue(type(d['foo']) == plist)
    self.assertTrue(type(d['bar']) == pset)
    self.assertTrue(type(d['baz']) == dict)  # Note that the child is a dict!
    # You probably shouldn't left-subtract by pdict, but you can. It converts any other pstar classes
    # to their python equivalents, but leaves pdicts alone.
    pd2 = pdict - pd
    self.assertTrue(type(pd2) == pdict)
    l = pdict - pd.foo
    self.assertTrue(type(l) == list)
    self.assertTrue(type(pd.foo) == plist)
    self.assertTrue(l == pd.foo)
    # Left division is also not recommended, but it works. It converts all other pstar classes
    # to their python equivalents, but leaves pdicts alone.
    pd2 = pdict / pd
    self.assertTrue(type(pd2) == pdict)
    self.assertTrue(type(pd2.foo) == list)
    self.assertTrue(type(pd2.bar) == set)
    self.assertTrue(type(pd2.baz) == pdict)
    d = pd - pstar
    self.assertTrue(type(d) == dict)
    self.assertTrue(type(d['foo']) == plist)
    self.assertTrue(type(d['bar']) == pset)
    self.assertTrue(type(d['baz']) == pdict)
    d = pstar - pd
    self.assertTrue(type(d) == dict)
    self.assertTrue(type(d['foo']) == plist)
    self.assertTrue(type(d['bar']) == pset)
    self.assertTrue(type(d['baz']) == pdict)
    d = pd / pstar
    self.assertTrue(type(d) == dict)
    self.assertTrue(type(d['foo']) == list)
    self.assertTrue(type(d['bar']) == set)
    self.assertTrue(type(d['baz']) == dict)
    d = pstar / pd
    self.assertTrue(type(d) == dict)
    self.assertTrue(type(d['foo']) == list)
    self.assertTrue(type(d['bar']) == set)
    self.assertTrue(type(d['baz']) == dict)
    foos = pstar.plist([pstar.pdict(foo=0, bar=0), pstar.pdict(foo=1, bar=1), pstar.pdict(foo=2, bar=0)])


  def test_from_docs_pstar_ptuple(self):
    pt = ptuple((1, 2.0, 'three'))
    pt = ptuple[1, 2.0, 'three']
    t1 = tuple([1, 2.0, 'three'])
    pt = ptuple * t1
    self.assertTrue(type(t1) == tuple)
    self.assertTrue(type(pt) == ptuple)
    self.assertTrue(pt == t1)
    t2 = pt / ptuple
    self.assertTrue(type(t2) == tuple)
    self.assertTrue(t2 == t1)


  def test_from_docs_pstar_ptuple_qj(self):
    log_fn = qj.LOG_FN
    with mock.patch('logging.info') as mock_log_fn:
      qj.LOG_FN = mock_log_fn
      pt = ptuple([1, 2.0, 'three'])
      pt.qj('pt')
      # Logs:
      # qj: <calling_module> calling_function: pt <2910>: (1, 2.0, 'three')
    qj.LOG_FN = log_fn
    qj.COLOR = True


# pylint: enable=line-too-long
if __name__ == '__main__':
  unittest.main()
