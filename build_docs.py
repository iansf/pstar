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
import glob
import inspect
import os
import re
import types

from qj_global import qj
import pstar
from pstar import *


SKIP_SYMBOLS = plist['pstar.pstar',]
PUBLICIZE_SYMBOLS = plist[
    '__init__',
    '_',
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
    '__str__',
]

API_DOC_TEMPLATE = """
<<full_signature>>

<<doc>>

<<children>>

<<source>>
""".strip()

symbols = defaultpdict(lambda: defaultpdict(str))


def cwd():
  return os.path.dirname(os.path.realpath(__file__))


def url_for(name):
  return './%s.md' % name.replace('.', '_')


def path_for(name):
  return os.path.join(cwd(), 'docs', '%s.md' % name.replace('.', '_'))


def bread_crumbs(symbol):
  symbol_parts = symbol[['name']].split('.').apply(plist).ungroup()[:-1]
  final_part = '%s`%s%s`' % ('.' if len(symbol_parts) else '', symbol.name.split('.')[-1], symbol.signature)
  return '.'.join(('[`' + symbol_parts + '`]({})').format(
      symbol_parts.pfill(1).apply(lambda i, sym_parts: url_for('.'.join(sym_parts[:i])), sym_parts=symbol_parts.aslist())
  )) + final_part


def full_signature(symbol):
  return '# %s' % bread_crumbs(symbol)


def _make_links(text_md, exclude=''):
  prefer = '.'.join(exclude.split('.')[:2])  # Prefer referencing objects from the same class.
  key_fn = lambda x: str(x.count('.')) + ('a' + x if x.startswith(prefer) else x)  # Sort by shortest depth symbols, then by symbols from the same class.
  return (symbols.peys() != exclude).sortby(key=key_fn).split('.')._[-1].puniq().root().reduce(lambda s, x: re.sub(r'(^|[^[])`%s`' % x.split('.')[-1], r'\1[`%s`](%s)' % (x.split('.')[-1], url_for(x)), s), text_md)[0]


def short_doc(symbol):
  return _make_links(symbol.short_doc, symbol.name)


def doc(symbol):
  return _make_links(symbol.doc, symbol.name)


def child_item(symbol, parent_name, base_depth):
  return (('____\n\n' if symbol.name.count('.') == 1 else '')
          + ('#' * (base_depth + len(symbol.name.replace(parent_name + '.', '').split('.'))))
          + ' [`%s%s`](%s)\n\n%s' % (symbol.name, symbol.signature, url_for(symbol.name), short_doc(symbol)))


def _get_children(symbol, base_depth):
  key_fn = lambda x: x.replace('__init__', '0__init__')  # Move __init__ functions to the top of the list of children.
  return '\n\n'.join(symbols[(symbols.peys() != symbol.name).startswith(symbol.name + '.').filter().sortby(key=key_fn)].apply(child_item, symbol.name, base_depth))


def children(symbol):
  children = _get_children(symbol, base_depth=2)
  return '## Children:\n\n%s' % children if children else ''


def source(symbol):
  return ('## [Source](%s)' % symbol.source) if symbol.source else ''


def build_api_doc(symbol):
  return process_template(API_DOC_TEMPLATE, symbol)


def basic_class_use(symbol):
  classes = symbols[(symbols.peys().split('.').apply(len) == 1 + plist(symbol.name.split('.')).plen()).startswith(symbol.name).filter()]
  return '\n\n'.join('### Basic [`' + classes.name.split('.')._[-1] + '`](' + classes.name.apply(url_for) + ') use:\n\n' + classes.apply(doc))


def api_overview(symbol):
  return 'Links for detailed documentation are below.\n\n%s\n\n' % _get_children(symbol, base_depth=2)


def tests_for(symbol):
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
  test_bodies = plist(symbol.doc.split('\n')).apply(line_of_code_or_blank) != ''
  test_bodies = inspect.cleandoc('\n'.join(test_bodies))  # Strips minimum number of spaces from all but first line.
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
    return ("""
  def test_from_docs_%s(self):
    %s
    """ % (symbol.name.replace('.', '_'), test_bodies)).rstrip()

  return ''


def public_symbols_for(obj):
  if obj.__name__ == '__init__' or isinstance(obj, types.MethodType):
    return plist()
  return plist(dir(obj)).filter(lambda s: not s.startswith('_') or s in PUBLICIZE_SYMBOLS).apply(lambda s: getattr(obj, s)).uproot()


def docs_for(obj):
  doc = inspect.getdoc(obj)
  blank_line = '\n                          \n'
  doc_lines = plist(doc.replace('Args:', '**Args:**')
                       .replace('Returns:', '**Returns:**\n')
                       .replace('Raises:', '**Raises:**')
                       .replace('Examples:', '**Examples:**')
                       .replace('\n\n', blank_line)
                       .split('\n'))
  short, body = doc_lines[0], doc_lines[1:]

  min_spaces = body.apply(lambda s: re.match('^\s*', s)).group(0).apply(len).append(100).wrap().np().min()[0]
  body = body._[min_spaces::1].rstrip()

  def maybe_indent_line(line):
    if plist['**Args:**', '**Returns:**', '**Raises:**'].any(lambda s: s in line):
      maybe_indent_line.indentation_block = True
    elif maybe_indent_line.indentation_block:
      line = '>  ' + line if line.strip() else line
      line = re.sub('^(\s*)>(\s+)([^\s:]+):', r'\n\1>\2**`\3`**:', line)
    return line
  maybe_indent_line.indentation_block = False

  body = body.apply(maybe_indent_line).uproot()

  return plist['\n'.join([short] + body.aslist()), short]


def signature_for(obj):
  signature = ''
  try:
    signature = inspect.formatargspec(*inspect.getargspec(obj))
  except Exception as e:
    try:
      signature = '(%s)' % inspect.getmro(obj)[1].__name__
    except Exception as e:
      pass
  return signature


def source_for(obj):
  filename = inspect.getsourcefile(obj).replace(cwd() + '/', '')
  lines = inspect.getsourcelines(obj)
  return '../%s#L%d-L%d' % (filename, lines[1], lines[1] + len(lines[0]))


def symbol_for(obj, name):
  symbol = symbols[name]
  symbol.name = name
  symbol.signature = signature_for(obj)
  symbol.source = source_for(obj)
  symbol[['doc', 'short_doc']] = docs_for(obj)
  symbol.tests = tests_for(symbol)
  return symbol


def process_template(template, symbol):
  sections = plist(re.findall('<<([^\s]+)>>', template))
  return ('<<' + sections + '>>').reduce(
      lambda s, l, section: s.replace(l, globals()[section](symbol)),
      template,
      sections).apply(_make_links, symbol.name)[0]


def collect_docs_and_tests(obj, base_name, full_base_name):
  try:
    if (not obj.__name__.startswith(base_name) and not obj.__module__.startswith(base_name)) or obj.__name__ in SKIP_SYMBOLS:
      return
    full_name = '.'.join(plist[full_base_name, obj.__name__] != '')
    if full_name in symbols:
      raise RuntimeError('Found duplicate symbol: %s' % full_name)
    symbol_for(obj, full_name)
    (public_symbols_for(obj) != obj).apply(collect_docs_and_tests, base_name, full_name)
  except AttributeError as e:
    # qj(str(e), 'Error processing %s' % str(obj))
    pass


def write_readme_md():
  plist(glob.glob(os.path.join(cwd(), 'docs', '*'))).apply(os.remove)

  readme_template_path = os.path.join(cwd(), 'README.md.template')
  readme_path = os.path.join(cwd(), 'docs', 'README.md')

  with open(readme_template_path, 'r') as f:
    template = f.read()

  docs_md = process_template(template, symbols[pstar.__name__])

  with open(readme_path, 'w') as f:
    f.write(docs_md)


def write_api_md():
  with symbols.peys().apply(path_for).apply(open, 'w') as files:
    files.write(symbols.palues().apply(build_api_doc))


def write_tests():
  tests_template_path = os.path.join(cwd(), 'pstar_test.py.template')
  tests_path = os.path.join(cwd(), 'pstar', 'tests', 'pstar_test.py')

  with open(tests_template_path, 'r') as f:
    template = f.read()

  template = template.replace('### <<doc_tests>> ###', '\n\n'.join(symbols.palues().tests.uproot() != ''))

  with open(tests_path, 'w') as f:
    f.write(template)


def build_docs():
  collect_docs_and_tests(pstar, pstar.__name__, '')

  write_readme_md()
  write_api_md()
  write_tests()


if __name__ == '__main__':
  build_docs()