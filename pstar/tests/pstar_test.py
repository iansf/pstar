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
    self.assertEqual(pl, [0, 1, 2, 3])

  def test_plist_init_depth(self):
    pl = plist([x for x in range(4)], depth=3)
    self.assertEqual(pl, [[[0, 1, 2, 3]]])

    pl.append__(4)
    self.assertEqual(pl, [[[0, 1, 2, 3, 4]]])

  def test_plist_of_defaultpdict(self):
    foos = plist([defaultpdict(lambda: defaultpdict(plist)) for _ in range(3)])

    foos.foo.bar.append_(3)
    self.assertEqual(foos.foo.bar, [3, 3, 3])

    foos.append(4)
    self.assertEqual(foos[-1], 4)

  def test_plist_of_pdict_filter_and_update(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])

    self.assertEqual(foos.foo, [0, 1, 2])
    self.assertEqual(foos.bar, [0, 1, 0])

    (foos.bar == 0).update(dict(baz=3))

    self.assertEqual((foos.bar == 0).baz, [3, 3])
    self.assertRaises(AttributeError, lambda: (foos.bar != 0).baz)

  def test_plist_of_pdict_filter_and_assign(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3

    self.assertEqual((foos.bar == 0).baz, [3, 3])
    self.assertRaises(AttributeError, lambda: (foos.bar != 0).baz)

  def test_plist_of_pdict_filter_and_read(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    self.assertEqual(foos.baz, [3, 6, 5])

  def test_plist_of_pdict_slow_n2_grouping(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    foos_by_bar = (plist([(foos.bar == bar) for bar in set(foos.bar)]))

    self.assertEqual(foos_by_bar,
                     [[{'baz': 3, 'foo': 0, 'bar': 0},
                       {'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'baz': 6, 'foo': 1, 'bar': 1}]])

  def test_plist_of_pdict_fast_groupby(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    foos_by_bar = foos.bar.groupby()

    self.assertEqual(foos_by_bar,
                     [[{'baz': 3, 'foo': 0, 'bar': 0},
                       {'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'baz': 6, 'foo': 1, 'bar': 1}]])

  def test_plist_of_pdict_groupby_filter(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6
    foos_by_bar = foos.bar.groupby()

    baz = foos_by_bar.baz.np_().sum()

    self.assertEqual(baz, [[3, 5], [6]])

    max_baz = baz[baz.np().argmax().apply(np.expand_dims, -1).tolist()]

    self.assertEqual(max_baz, [[5], [6]])
    self.assertEqual(baz == max_baz,
                    [[{'baz': 5, 'foo': 2, 'bar': 0}],
                     [{'baz': 6, 'foo': 1, 'bar': 1}]])

    (baz == max_baz).bin = 13

    self.assertEqual(foos_by_bar,
                     [[{'baz': 3, 'foo': 0, 'bar': 0},
                       {'bin': 13, 'baz': 5, 'foo': 2, 'bar': 0}],
                      [{'bin': 13, 'baz': 6, 'foo': 1, 'bar': 1}]])

  def test_plist_of_pdict_and_filter(self):
    foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
    (foos.bar == 0).baz = 3 + (foos.bar == 0).foo
    (foos.bar == 1).baz = 6

    foos_by_bar = foos.bar.groupby()
    baz = foos_by_bar.baz.np_().sum()
    max_baz = baz[baz.np().argmax().apply(np.expand_dims, -1).tolist()]
    (baz == max_baz).bin = 13

    ((foos.bar == 0) & (foos.baz == 3)).qj('and filtered foos')
    self.assertEqual((foos.bar == 0) & (foos.baz == 3),
                     [{'baz': 3, 'foo': 0, 'bar': 0}])


"""

foos = plist([pdict(foo=i, bar=i % 2) for i in range(3)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6

foos_by_bar = foos.bar.groupby().qj('SPEEDY! GOOD!')
baz = foos_by_bar.baz.np_().qj('np').sum().qj('baz sum')
max_baz = baz[baz.np().argmax().apply(np.expand_dims, -1).tolist().qj('baz.argmax')].qj('baz[argmax]')
(baz == max_baz).qj('baz == max_baz').foo.qj('final foos').root().bin = 13

((foos.bar == 0) & (foos.baz == 3)).qj('and filtered foos')
_ = foos_by_bar.qj('foos_by_bar')

foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

foos_by_bar = foos.bar.groupby()

(foos_by_bar.bar == 0).qj('by_bar == 0')
(foos_by_bar.bar == 1).qj('by_bar == 1')
(foos_by_bar.bar == 2).qj('by_bar == 2')

foos_by_bar.qj('by_bar')
_ = foos_by_bar.join().qj('joined')

foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])

foos_by_bar = foos.bar.groupby().qj('by_bar')

(foos_by_bar.bar > 0).qj('by_bar > 0')
(foos_by_bar.bar != 1).qj('by_bar != 1')
(foos_by_bar.bar < 2).qj('by_bar < 2')
(foos_by_bar.bar <= 1).qj('by_bar <= 1')
(foos_by_bar.bar >= 1).qj('by_bar >= 1')

None

foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
foos_by_bar = foos.bar.groupby().qj('by_bar')

((foos_by_bar.bar == 0) & (foos_by_bar.bar == 1)).qj('by_bar == 0 & by_bar == 1')
((foos_by_bar.bar == 0) & (foos_by_bar.bar <= 1)).qj('by_bar == 0 & by_bar <= 1')

((foos_by_bar.bar == 0) | (foos_by_bar.bar == 1)).qj('by_bar == 0 | by_bar == 1')
((foos_by_bar.bar == 0) | (foos_by_bar.bar <= 1)).qj('by_bar == 0 | by_bar <= 1')

((foos_by_bar.bar == 0) ^ (foos_by_bar.bar == 1)).qj('by_bar == 0 ^ by_bar == 1')
((foos_by_bar.bar == 0) ^ (foos_by_bar.bar <= 1)).qj('by_bar == 0 ^ by_bar <= 1')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

foos.apply(len).qj('apply len')
foos.apply('keys').qj('apply keys')

None

foos = plist([pdict(foo=i, bar=i % 3) for i in range(5)])
foos_by_bar = foos.bar.groupby()
(foos_by_bar.bar == 0).qj('by_bar == 0').pshape().qj('pshape').root().nonempty().qj('by_bar == 0 nonempty')
None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

foos.bar.qj('bar').root().baz.qj('baz')
foos[('bar','baz')].qj('bar,baz')
foos.bar.preduce_eq().qj('bar.pred=').root().qj('bar.pred=.root')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root().qj('by_bar_baz')
by_bar_baz[('bar','baz')].qj('bar,baz')
by_bar_baz.bar.preduce_eq__().qj('bar.pred=').root().qj('bar.pred=.root')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

foos[:3].qj('foos[:3]').bar.qj('foos[:3].bar')
foos.bar[:3].qj('foos.bar[:3]').root().bar.qj('foos.bar[:3].root.bar')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).qj('sortby bar').groupby().qj('by_bar').baz.groupby().baz.qj('by_bar_baz.baz').sortby_().qj('by_bar_baz.baz.sortby').root().baz.qj('by_bar_baz.baz.sortby.root.baz').root().bar.qj('by_bar_baz.baz.sortby.root.bar').root()
by_bar_baz.qj('by_bar_baz').baz.qj('by_bar_baz.baz')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
by_bar_baz.qj('by_bar_baz')

by_bar_baz.apply(len, pepth=0).qj('len')
by_bar_baz.apply(len, pepth=1).qj('len_')
by_bar_baz.apply(len, pepth=2).qj('len__ (actually on internal pdicts)')

by_bar_baz.plen().qj('plen')
by_bar_baz.plen(2).qj('plen 2')
by_bar_baz.plen(-1).qj('plen -1')

by_bar_baz.rlen().qj('rlen')
by_bar_baz.rlen(2).qj('rlen 2')
by_bar_baz.rlen(-1).qj('rlen -1')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
by_bar_baz.qj('by_bar_baz')

by_bar_baz.pshape().qj('pshape')
by_bar_baz.pfill().qj('pfill')
by_bar_baz.pfill_().qj('pfill_')
by_bar_baz.pfill__().qj('pfill__')
by_bar_baz.pfill(-1).qj('pfill -1')
by_bar_baz.pfill(5).qj('pfill 5')
by_bar_baz.apply('pfill', -1, pepth=-1).qj('apply pfill(-1) pepth=-1 (useful for generating complete indices)')

qj(by_bar_baz.lfill(), 'lfill', l=lambda x: type(x))
qj(by_bar_baz.lfill_(), 'lfill_', l=lambda x: type(x))
qj(by_bar_baz.lfill__(), 'lfill__', l=lambda x: type(x))
qj(by_bar_baz.lfill(-1), 'lfill -1', l=lambda x: type(x))
qj(by_bar_baz.lfill(5), 'lfill 5', l=lambda x: type(x))
qj(by_bar_baz.apply('lfill', -1, pepth=-1), 'apply lfill(-1) pepth=-1 (useful for generating complete indices)', l=lambda x: type(x))

by_bar_baz.pleft().qj('pleft')
by_bar_baz.pleft_().qj('pleft_')
by_bar_baz.pleft__().qj('pleft__')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().baz.sortby_().root()
by_bar_baz.qj('by_bar_baz')

by_bar_baz.ungroup_().qj('bbb.ug_').ungroup().qj('bbb.ug_.ug')
by_bar_baz.ungroup(2).qj('bbb.ug^2')
by_bar_baz.ungroup(-1).qj('bbb.ug^-1')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().sortby_()
by_bar_baz.qj('by_bar_baz').values_like().qj('vals_like').values_like(11).qj('vals_like 11').root().values_like_(12).qj('vals_like_ 12').ungroup_().values_like('a').qj('ug.vals_like a').root().qj('root').values_like(by_bar_baz.foo + by_bar_baz.bar).qj('vals_like foo + bar')

None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

by_bar = foos.bar.groupby()
baz = by_bar.baz.np_().qj('np').sum().qj('baz sum')
max_baz = baz[baz.np().argmax().apply(np.expand_dims, -1).tolist().qj('baz.argmax')].qj('baz[argmax]')
(baz == max_baz).qj('baz == max_baz').foo.qj('final foos').root().bin = 13

_ = by_bar.qj('by_bar')
_ = by_bar.bin.groupby().qj('by_bar_bin')

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.sortby(reverse=True).groupby().baz.groupby().sortby_().root()

(by_bar_baz.bar == 0).qj('by_bar == 0').pshape().qj('pshape').root().nonempty().qj('by_bar == 0 nonempty')
(by_bar_baz.bar == 0).nonempty(2).qj('by_bar == 0 nonempty^2')
(by_bar_baz.bar == 0).nonempty(-1).qj('by_bar == 0 nonempty^-1').nonempty().qj('by_bar == 0 nonempty^-1 nonempty')
None

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

by_bar = foos.bar.sortby(reverse=True).groupby()
baz = by_bar.baz.np_().qj('np').sum().qj('baz sum')
(baz == baz.np().max()).qj('baz == max_baz').foo.qj('final foos').root().bin = 13

foos.remix().qj('foos remix()')
foos.remix('foo', 'baz', new_bin=foos.bin * 13).qj('foos remix(*a, **kw)')

by_bar.remix().qj('by_bar remix()')
by_bar_rm = by_bar.remix('foo', 'baz', new_bin=by_bar.bin * 13).qj('by_bar remix(*a, **kw)')

by_bar_rm.baz.qj('bbr.baz').root_().qj('bbr.baz.root_')

_ = by_bar.qj('by_bar')
by_bar_bin = by_bar.bin.groupby().qj('by_bar_bin')

qj(by_bar_rm.pd(), 'bbr.pd')
foos.pd(index='foo')

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

by_bar = foos.bar.groupby()
baz = by_bar.baz.np_().sum()
(baz == baz.np().max()).bin = 13

by_bar_bin = by_bar.qj('by_bar').bin.groupby().qj('by_bar_bin').bin.sortby__().root().qj('by_bar_bin.sort')
by_bar_bin.pd__().qj_('inner dataframes')

qj(by_bar_bin.ungroup_().qj('bb.ungroup').ungroup().qj('bb.ungroup.ungroup').pd(index='foo'), 'bb.ug.ug.pd')
qj(by_bar_bin.ungroup(2).qj('bb.ug^2').foo.sortby(key=lambda x: (x + 1) * ((x + 1) % 2) - (x + 1) * (x % 2), reverse=True).qj('bb.ug^2.sortby(evens->0->odds)').root().pd(index='foo'), 'bb.ug.ug.sortby.pd')

foos.pd(index='foo')

foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

by_bar = foos.bar.groupby()
baz = by_bar.baz.np_().sum()
(baz == baz.np().max()).bin = 13

by_bar.bin.groupby().qj('by_bar_bin').baz.groupby().qj('bb.baz.gb').ungroup(-1).qj('ungroup all').pd()

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
