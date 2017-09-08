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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import re
import sys

import unittest
import mock

import numpy as np

from pstar import *
from qj import qj

DEBUG_TESTS = False


# pylint: disable=line-too-long
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

  def test_empty_plist(self):
    self.assertFalse(plist())

  def test_empty_plist_ungroup(self):
    self.assertFalse(plist().ungroup(-1))

  def test_plist_init(self):
    pl = plist([x for x in range(4)])
    self.assertEqual(pl.aslist(),
                     [0, 1, 2, 3])

  def test_plist_init_depth(self):
    pl = plist([x for x in range(4)], depth=3)
    self.assertEqual(pl.aslist(),
                     [[[0, 1, 2, 3]]])

    pl.append__(4)
    self.assertEqual(pl.aslist(),
                     [[[0, 1, 2, 3, 4]]])

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

  def test_plist_of_pdict_preduce_eq(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.bar.preduce_eq().aslist(),
                     [0, 1])
    self.assertEqual(foos.bar.preduce_eq().root().aslist(),
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

  def test_plist_of_pdict_groupby_preduce_eq(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
    self.assertEqual(by_bar_baz.bar.preduce_eq__().aslist(),
                     [[[1]], [[0], [0], [0]]])

    # TODO(iansf): This test fails because interior plists can't change the root of the outer plist.
    self.assertEqual(by_bar_baz.bar.preduce_eq__().root().aslist(),
                     [[[{'baz': 6, 'foo': 1, 'bar': 1}]],
                      [[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])

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

    self.assertEqual(by_bar_baz.plen().aslist(),
                     [2])
    self.assertEqual(by_bar_baz.plen(2).aslist(),
                     [[4]])
    self.assertEqual(by_bar_baz.plen(-1).aslist(),
                     [[[5]]])

  def test_plist_of_pdict_groupby_groupby_rlen(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.rlen().aslist(),
                     [2])
    self.assertEqual(by_bar_baz.rlen(2).aslist(),
                     [[1], [3]])
    self.assertEqual(by_bar_baz.rlen(-1).aslist(),
                     [[[2]], [[3]]])

  def test_plist_of_pdict_groupby_groupby_pshape(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.pshape().aslist(),
                     [[[2]], [[1], [1], [1]]])
    self.assertEqual(by_bar_baz.pshape_().aslist(),
                     [[[2]], [[1], [1], [1]]])
    self.assertEqual(by_bar_baz.pshape__().aslist(),
                     [[[2]], [[1], [1], [1]]])

  def test_plist_of_pdict_groupby_groupby_pfill(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.pfill().aslist(),
                     [[[1, 2]], [[3], [4], [5]]])
    self.assertEqual(by_bar_baz.pfill(-1).aslist(),
                     [[[0, 1]], [[2], [3], [4]]])
    self.assertEqual(by_bar_baz.pfill(5).aslist(),
                     [[[6, 7]], [[8], [9], [10]]])
    self.assertEqual(by_bar_baz.pfill_().aslist(),
                     [[[1, 2]], [[1], [2], [3]]])
    self.assertEqual(by_bar_baz.pfill__().aslist(),
                     [[[1, 2]], [[1], [1], [1]]])
    # Generates a complete index plist into the source plist.
    self.assertEqual(by_bar_baz.apply('pfill', -1, pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])
    # Better way of generating a complete index with pfill.
    self.assertEqual(by_bar_baz.pfill(-1, pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])

  def test_plist_of_pdict_groupby_groupby_lfill(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    self.assertEqual(by_bar_baz.lfill(),
                     [[[1, 2]], [[3], [4], [5]]])
    self.assertNotIsInstance(by_bar_baz.lfill(), plist)
    self.assertEqual(by_bar_baz.lfill(-1),
                     [[[0, 1]], [[2], [3], [4]]])
    self.assertEqual(by_bar_baz.lfill(5),
                     [[[6, 7]], [[8], [9], [10]]])

    self.assertEqual(by_bar_baz.lfill_().aslist(),
                     [[[1, 2]], [[1], [2], [3]]])
    self.assertIsInstance(by_bar_baz.lfill_(), plist)
    self.assertEqual(by_bar_baz.lfill__().aslist(),
                     [[[1, 2]], [[1], [1], [1]]])

    self.assertEqual(by_bar_baz.lfill__().aslist(),
                     by_bar_baz.lfill(pepth=2).aslist())

    # Generates a complete index list into the source plist.
    self.assertEqual(by_bar_baz.apply('lfill', -1, pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])
    self.assertIsInstance(by_bar_baz.apply('lfill', -1, pepth=-1), plist)

    self.assertEqual(by_bar_baz.apply('lfill', -1, pepth=-1).aslist(),
                     by_bar_baz.lfill(-1, pepth=-1).aslist())

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

    self.assertEqual(by_bar_baz.ungroup_().aslist(),
                     [[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}],
                      [{'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}]])
    self.assertEqual(by_bar_baz.ungroup_().ungroup().aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}])
    self.assertEqual(by_bar_baz.ungroup(2).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}])
    self.assertEqual(by_bar_baz.ungroup(-1).aslist(),
                     [{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}, {'baz': 1, 'foo': 2, 'bar': 0}, {'baz': 2, 'foo': 4, 'bar': 0}, {'baz': 3, 'foo': 0, 'bar': 0}])

  def test_plist_of_pdict_groupby_groupby_ungroup_root_uproot(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    (foos.bar == 1).baz = 6

    by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()

    # TODO(iansf): Think about which of these two outputs should be the result of ungroup_.root.
    self.assertEqual(by_bar_baz.ungroup_().root().aslist(),
                     [[[{'baz': 6, 'foo': 1, 'bar': 1}, {'baz': 6, 'foo': 3, 'bar': 1}]],
                      [[{'baz': 1, 'foo': 2, 'bar': 0}],
                       [{'baz': 2, 'foo': 4, 'bar': 0}],
                       [{'baz': 3, 'foo': 0, 'bar': 0}]]])
    self.assertEqual(by_bar_baz.ungroup_().uproot().root().aslist(),
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
    self.assertEqual(by_bar_baz.ungroup_().values_like('a').aslist(),
                     [['a', 'a'], ['a', 'a', 'a']])
    self.assertEqual(by_bar_baz.values_like(by_bar_baz.foo + by_bar_baz.bar).aslist(),
                     [[[2, 4]], [[2], [4], [0]]])

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
                      ]])

  def test_plist_of_pdict_groupby_groupby_sortby_ungroup_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby().bin.sortby__().root()

    self.assertEqual(by_bar_bin.ungroup_().ungroup().aslist(),
                     [{'bin': -1, 'baz': 3, 'foo': 0, 'bar': 0},
                      {'bin': -1, 'baz': 5, 'foo': 2, 'bar': 0},
                      {'bin': 13, 'baz': 7, 'foo': 4, 'bar': 0},
                      {'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1},
                      {'bin': 13, 'baz': 6, 'foo': 3, 'bar': 1}])

    self.assertEqual(str(by_bar_bin.ungroup_().ungroup().pd(index='foo')),
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

      rmx.bam.qj(rmx.bun.ungroup(-1).preduce_eq().pstr().qj('bun'), n=1, pepth=1)
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar_test> test_sample_data_analysis_flow: bun <\d+>: \['10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0'\]")),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:  10 \(shape \(min \(mean std\) max\) hist\) <\d+>: \(\(91,\), \(0\.0, \(8\.4\d*, 5\.0\d*\), 21\.0\), array\(\[22, 23, 29, 11,  6\]\)')),
              mock.call(
                  RegExp(r"qj: <pstar_test> test_sample_data_analysis_flow:  9 \(shape \(min \(mean std\) max\) hist\) <\d+>: \(\(91,\), \(0\.0, \(8.3\d+, 5.1\d+\), 20.0\), array\(\[24, 12, 34, 14,  7\]\)")),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 12)
      mock_log_fn.reset_mock()


      params = (rmx.bam == rmx.bam.np().max())[tuple(['bun'] + list(fields))].qj('max-yielding params').pshape().qj('maxes ps').root()
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r"qj: <pstar_test> test_sample_data_analysis_flow:   max-yielding params <\d+>: \[\[\(10, 11, 1\), \(10, 11, 1\), \(10, 11, 1\)\], ")),
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:    maxes ps <\d+>: \[\[3\], \[5\], \[1\], \[2\], \[1\], \[1\], \[2\], \[1\], \[1\], \[1\], \[7\]\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 2)
      mock_log_fn.reset_mock()

      rmx_x = rmx.bun.preduce_eq(pepth=1).ungroup().qj('rmx_x')
      mock_log_fn.assert_has_calls(
          [
              mock.call(
                  RegExp(r'qj: <pstar_test> test_sample_data_analysis_flow:     rmx_x <\d+>: \[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0\]')),
          ],
          any_order=False)
      self.assertEqual(mock_log_fn.call_count, 1)
      mock_log_fn.reset_mock()

      rmx.ungroup(-1).bun.groupby().bam.join().np_().apply(lambda y, x: [qj((x_, np.mean(y_))) for x_, y_ in zip(x, y)], rmx_x)
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
         .np().mean().qj('means').join().apply(
              lambda y, x: [qj((x_, y_)) for x_, y_ in zip(x, y)], rmx_x
         )
         .root()[0].root().apply('__getslice___', 0, 10).qj('bam top 10').join()
         .root()[0].root().__getslice___(0, 10).qj('bam top 10').join()
         .root()[0].root().__getslice__(0, 10, pepth=1).qj('bam top 10').join()
         .root()[0].root().apply(type).qj('bam types')
        )
      else:
        (rmx.ungroup(-1)[fields].sortby().root().bun.groupby()
         .bam.np_().max().sortby_(reverse=True).np().uproot().shape.qj('shape').root()
         .np().mean().qj('means').join().apply(
              lambda y, x: [qj((x_, y_)) for x_, y_ in zip(x, y)], rmx_x
         )
         .root()[0].root().apply('__getitem___', slice(0, 10)).qj('bam top 10').join()
         .root()[0].root().__getitem___(slice(0, 10)).qj('bam top 10').join()
         .root()[0].root().__getitem__(slice(0, 10), pepth=1).qj('bam top 10').join()
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

  @unittest.skip('slow')
  def test_plist_of_pdict_timing(self):
    qj(tic=1)
    large_input = [pdict(foo=i, bar=i % 2, bin=i % 13, bun=i % 11) for i in range(100000)]
    qj(toc=-1, tic=1)

    foos = plist(large_input)
    qj(toc=-1, tic=1)

    (foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
    qj(tic=2)
    (foos.bar == 1).baz = 6
    qj(toc=-1, tic=1)

    fields = ('bin', 'bar')
    by = foos[fields].sortby().groupby().bun.sortby_().groupby()
    qj(toc=1, tic=2)
    by.baz = by.foo % (by.bin + by.bun + 1)
    qj(toc=1, tic=3)

    by.baz.qj(by[fields].preduce_eq__().ungroup_().pstr(), n=10, pepth=2)
    qj(toc=1)



# pylint: enable=line-too-long
if __name__ == '__main__':
  unittest.main()
