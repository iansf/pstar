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
"""Build README.md.

Run with:
```bash
python build_docs.py
```
"""
import inspect
import os
import re
import types

from qj_global import qj
import pstar
from pstar import *


SECTIONS = plist['advanced_usage',]
SKIP_SYMBOLS = plist['pstar.pstar',]
PUBLICIZE_SYMBOLS = plist[
    '__init__',
    '_',
    '_build_comparator',
    '_build_logical_op',
    '_build_binary_op',
    '_build_unary_op',
    '_call_attr',
    '_ensure_len',
    '_merge_indices',
    '__getattribute__',
    '__getattr__',
    '__getitem__',
    '__getslice__',
    '__setattr__',
    '__setitem__',
    '__setslice__',
    '__delattr__',
    '__delitem__',
    '__delslice__',
    '__call__',
    '__contains__',
    '__cmp__',
    '__and__',
    '__add__',
    '__neg__',
    '__enter__',
    '__exit__',
]

tests_from_docs = plist()


def extract_tests(name, doc):
  code_start = '```python'
  code_end = '```'
  def line_of_code_or_blank(line):
    if code_start in line:
      line_of_code_or_blank.in_code_block = True
      return ''
    if code_end in line:
      line_of_code_or_blank.in_code_block = False
      return ''
    if line_of_code_or_blank.in_code_block:
      return line
    return ''
  line_of_code_or_blank.in_code_block = False
  test_bodies = plist(doc.split('\n')).apply(line_of_code_or_blank) != ''
  test_bodies = process_doc('\n'.join(test_bodies))  # Strips minimum number of spaces from all but first line.
  test_bodies = plist(test_bodies.split('\n'))
  if test_bodies.startswith('# Logs:').any():
    test_bodies = '  ' + test_bodies
    test_bodies.insert(
        0,
        'log_fn = qj.LOG_FN\n' +
        'with mock.patch(\'logging.info\') as mock_log_fn:\n' +
        '  qj.LOG_FN = mock_log_fn'
    ).append(
        'qj.LOG_FN = log_fn\n' +
        'qj.COLOR = True')
    test_bodies = plist('\n'.join(test_bodies).split('\n'))

  if test_bodies.any(lambda s: 'plt.show()' in s):
    test_bodies = '  ' + test_bodies
    test_bodies.insert(0, 'with mock.patch(\'matplotlib.pyplot.show\'):')
    test_bodies = plist('\n'.join(test_bodies).split('\n'))
  test_bodies = '\n'.join('    ' + test_bodies).strip().replace('assert (', 'self.assertTrue(')

  if test_bodies:
    test = ("""
  def test_from_docs_%s(self):
    %s
    """ % (name.replace('.', '_'), test_bodies)).rstrip()

    tests_from_docs.append(test)

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

def get_signature(obj, full_name):
  signature = ''
  return full_name #+ '(' + signature + ')'

def get_docs(obj, depth, base_name, full_base_name):
  try:
    if (not obj.__name__.startswith(base_name) and not obj.__module__.startswith(base_name)) or obj.__name__ in SKIP_SYMBOLS:
      return ''
    full_name = '.'.join(plist[full_base_name, obj.__name__] != '')
    docs = '\n%s `%s`\n\n%s' % ('#' * depth, get_signature(obj, full_name), process_doc(inspect.getdoc(obj)))
    extract_tests(full_name, docs)
    subdocs = (find_public_symbols(obj) != obj).apply(get_docs, depth + 1, base_name, full_name).uproot() != ''
    return docs + '\n\n'.join(subdocs)
  except AttributeError as e:
    # qj(str(e), 'Error processing %s' % str(obj))
    return ''

def advanced_usage(base_path):
  return get_docs(pstar, 3, base_path, '')

def build_docs():
  cwd = os.path.dirname(os.path.realpath(__file__))
  readme_template_path = os.path.join(cwd, 'README.md.template')
  readme_path = os.path.join(cwd, 'README.md')

  with open(readme_template_path, 'r') as f:
    template = f.read()

  section_labels = '<<' + SECTIONS + '>>'

  template = pdict(s=template)
  section_labels.apply(
      lambda l, section: template.update(s=template.s.replace(l, globals()[section](pstar.__name__))),
      SECTIONS)

  with open(readme_path, 'w') as f:
    f.write(template.s)

  tests_template_path = os.path.join(cwd, 'pstar_test.py.template')
  tests_path = os.path.join(cwd, 'pstar', 'tests', 'pstar_test.py')

  with open(tests_template_path, 'r') as f:
    template = f.read()

  template = template.replace('### <<doc_tests>> ###', '\n\n'.join(tests_from_docs))

  with open(tests_path, 'w') as f:
    f.write(template)



if __name__ == '__main__':
  build_docs()