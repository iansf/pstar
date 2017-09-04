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


# pylint: enable=line-too-long
if __name__ == '__main__':
  unittest.main()
