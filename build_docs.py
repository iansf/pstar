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
import os
import re
import types

from qj_global import qj
import pstar
from pstar import *


SECTIONS = plist['advanced_usage',]
SKIP_SYMBOLS = plist['pstar.pstar',]
PUBLICIZE_SYMBOLS = plist['__init__', '_']


def find_public_symbols(obj):
  if obj.__name__ == '__init__' or isinstance(obj, types.MethodType):
    return plist()
  return plist(dir(obj)).filter(lambda s: not s.startswith('_') or s in PUBLICIZE_SYMBOLS).apply(lambda s: getattr(obj, s)).uproot()

def process_doc(doc):
  blank_line = '\n                          \n'
  doc_lines = plist(doc.replace('\n\n', blank_line).split('\n'))
  short, body = doc_lines[0], doc_lines[1:]

  min_spaces = body.apply(lambda s: re.match('^\s*', s)).group(0).apply(len).append(100).join().np().min()[0]
  body = body._[min_spaces::1].rstrip().aslist()

  return '\n'.join([short] + body)

def get_docs(obj, depth, base_name, full_base_name):
  try:
    if (not obj.__name__.startswith(base_name) and not obj.__module__.startswith(base_name)) or obj.__name__ in SKIP_SYMBOLS:
      return ''
    full_name = '.'.join(plist[full_base_name, obj.__name__] != '')
    docs = '%s %s\n\n%s' % ('#' * depth, full_name, process_doc(obj.__doc__))
    subdocs = (find_public_symbols(obj) != obj).apply(get_docs, depth + 1, base_name, full_name).uproot() != ''
    return docs + '\n\n'.join(subdocs)
  except AttributeError as e:
    # qj(str(e), 'Error processing %s' % str(obj))
    return ''

def advanced_usage(base_path):
  return get_docs(pstar, 3, base_path, '')

def build_docs():
  cwd = os.path.dirname(os.path.realpath(__file__))
  template_path = os.path.join(cwd, 'README.md.template')
  readme_path = os.path.join(cwd, 'README.md')

  with open(template_path, 'r') as f:
    template = f.read()

  section_labels = '<<' + SECTIONS + '>>'

  template = pdict(s=template)
  section_labels.apply(
      lambda l, section: template.update(s=template.s.replace(l, globals()[section](pstar.__name__))),
      SECTIONS)

  with open(readme_path, 'w') as f:
    f.write(template.s)


if __name__ == '__main__':
  build_docs()