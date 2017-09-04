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

DEBUG_TESTS = False


# pylint: disable=line-too-long
class RegExp(object):

  def __init__(self, pattern, flags=0):
    self._p = pattern
    self._f = flags

  def __eq__(self, o):
    if DEBUG_TESTS:
      print('%s: \'%s\'' % (str(self), str(o)))
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

    self.assertEqual(foos.apply('keys').aslist(),
                     [['baz', 'foo', 'bar'],
                      ['baz', 'foo', 'bar'],
                      ['baz', 'foo', 'bar'],
                      ['baz', 'foo', 'bar'],
                      ['baz', 'foo', 'bar']])

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

    # Generates a complete index list into the source plist.
    self.assertEqual(by_bar_baz.apply('lfill', -1, pepth=-1).aslist(),
                     [[[0, 1]], [[0], [0], [0]]])
    self.assertIsInstance(by_bar_baz.apply('lfill', -1, pepth=-1), plist)

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

    self.assertEqual(str(by_bar.pd()),
                     '                                               0  \\\n'
                     "0  {u'bin': 13, u'baz': 6, u'foo': 1, u'bar': 1}   \n"
                     "1  {u'bin': -1, u'baz': 3, u'foo': 0, u'bar': 0}   \n"
                     '\n'
                     '                                               1  \\\n'
                     "0  {u'bin': 13, u'baz': 6, u'foo': 3, u'bar': 1}   \n"
                     "1  {u'bin': -1, u'baz': 5, u'foo': 2, u'bar': 0}   \n"
                     '\n'
                     '                                               2  \n'
                     '0                                           None  \n'
                     "1  {u'bin': 13, u'baz': 7, u'foo': 4, u'bar': 0}  ")

  def test_plist_of_pdict_groupby_groupby_pd(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos.bin = -1

    by_bar = foos.bar.sortby(reverse=True).groupby()
    baz = by_bar.baz.np_().sum()
    (baz == baz.np().max()).bin = 13

    by_bar_bin = by_bar.bin.groupby()

    self.assertEqual(str(by_bar_bin.pd()),
                     '                                                   0  \\\n'
                     "0  [{u'bin': 13, u'baz': 6, u'foo': 1, u'bar': 1}...   \n"
                     "1  [{u'bin': -1, u'baz': 3, u'foo': 0, u'bar': 0}...   \n"
                     '\n'
                     '                                                 1  \n'
                     '0                                             None  \n'
                     "1  [{u'bin': 13, u'baz': 7, u'foo': 4, u'bar': 0}]  ")

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


"""
foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

by_bar = foos.bar.groupby()
baz = by_bar.baz.np_().sum()
(baz == baz.np().max()).bin = 13
df = qj(by_bar.ungroup().pd(), 'by_bar')
qj(df[(df.bar == 0) & (df.bin == -1)], 'df[bar == 0 and bin == -1]')

qj(((by_bar.qj('by_bar').bar == 0).qj('bar == 0', l=lambda x: len(x)) & (by_bar.bin == -1).qj('bin == -1', l=lambda x: len(x))).qj('bar == 0 and bin == -1').ungroup().pd(), 'df')
qj(((by_bar.bar == 0) | (by_bar.bin == -1)).qj('bar == 0 or bin == -1').ungroup().pd(), 'df')
qj(((by_bar.bar == 0) ^ (by_bar.bin == -1)).qj('bar == 0 xor bin == -1').ungroup().pd(), 'df')
qj(((by_bar.bar == 0) & (by_bar.bar == 0)).qj('bar == 0 and bar == 0').ungroup().pd(), 'df')

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

by_bar = foos.bar.groupby()
baz = by_bar.baz.np_().sum()
(baz == baz.np().max()).bin = 13

by_bar_bin = by_bar.bin.groupby().qj('by_bar_bin')
by_bar_bin.foo.qj__('CORRECT: foos by_bar_bin')
by_bar_bin.foo.apply(qj, 'SHOULD MATCH: foos by_bar_bin', pepth=1)
by_bar_bin.foo.apply_(qj, 'SHOULD MATCH_: foos by_bar_bin')
by_bar_bin.foo.apply(qj, 'PAINFUL *args bin=' + by_bar_bin.bar.apply(str, pepth=2) + ' baz=' + by_bar_bin.baz.apply(str, pepth=2), pepth=1)
by_bar_bin.foo.apply(qj, s='PAINFUL **kwargs bin=' + by_bar_bin.bar.apply(str, pepth=2) + ' baz=' + by_bar_bin.baz.apply(str, pepth=2), pepth=1)

by_bar_bin.foo.apply(qj, 'NICE *a bin=' + by_bar_bin.bar.pstr() + ' baz=' + by_bar_bin.baz.pstr(), pepth=1)
by_bar_bin.foo.apply(qj, s='NICE **kw bin=' + by_bar_bin.bar.pstr() + ' baz=' + by_bar_bin.baz.pstr(), pepth=1)

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6
foos.qj('foos')

(foos == foos[:1]).qj('foos == foos[:1]')
(foos != foos[:1]).qj('foos != foos[:1]')

(foos == foos[:2]).qj('foos == foos[:2]')
(foos != foos[:2]).qj('foos != foos[:2]')

(foos == foos[1:2]).qj('foos == foos[1:2]')
(foos != foos[1:2]).qj('foos != foos[1:2]')

(foos == foos[1:]).qj('foos == foos[1:]')
(foos != foos[1:]).qj('foos != foos[1:]')

(foos.foo >= foos[:1].foo).qj('foos.foo >= foos[:1].foo')
(foos.foo <= foos[:1].foo).qj('foos.foo <= foos[:1].foo')

(foos.foo >= foos[1:2].foo).qj('foos.foo >= foos[1:2].foo')
(foos.foo <= foos[1:2].foo).qj('foos.foo <= foos[1:2].foo')

(foos.foo >= foos[1:4].foo).qj('foos.foo >= foos[1:4].foo')
(foos.foo <= foos[1:4].foo).qj('foos.foo <= foos[1:4].foo')

(foos.foo > foos[:1].foo).qj('foos.foo > foos[:1].foo')
(foos.foo < foos[:1].foo).qj('foos.foo < foos[:1].foo')

(foos.foo > foos[1:2].foo).qj('foos.foo > foos[1:2].foo')
(foos.foo < foos[1:2].foo).qj('foos.foo < foos[1:2].foo')

(foos.foo > foos[1:4].foo).qj('foos.foo > foos[1:4].foo')
(foos.foo < foos[1:4].foo).qj('foos.foo < foos[1:4].foo')

by_bar_baz = foos.bar.sortby().groupby().baz.groupby().sortby_().qj('by_bar_baz')

(by_bar_baz == by_bar_baz[:1]).qj('by_bar_baz == by_bar_baz[:1]')
(by_bar_baz != by_bar_baz[:1]).qj('by_bar_baz != by_bar_baz[:1]')

(by_bar_baz == by_bar_baz[:2]).qj('by_bar_baz == by_bar_baz[:2]')
(by_bar_baz != by_bar_baz[:2]).qj('by_bar_baz != by_bar_baz[:2]')

(by_bar_baz.foo >= by_bar_baz[:1].foo).qj('by_bar_baz.foo >= by_bar_baz[:1].foo')
(by_bar_baz.foo <= by_bar_baz[:1].foo).qj('by_bar_baz.foo <= by_bar_baz[:1].foo')

(by_bar_baz.foo >= by_bar_baz[:2].foo).qj('by_bar_baz.foo >= by_bar_baz[:2].foo (switches to element-wise comparison)')
(by_bar_baz.foo <= by_bar_baz[:2].foo).qj('by_bar_baz.foo <= by_bar_baz[:2].foo (switches to element-wise comparison)')

None
"""

# pylint: enable=line-too-long
if __name__ == '__main__':
  unittest.main()
