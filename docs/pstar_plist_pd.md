# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pd(self, *args, **kwargs)`

Converts `self` into a `pandas.DataFrame`, forwarding passed args.

**Examples:**
```python
foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = -1

assert (foos.aslist() ==
        [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
         {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 1},
         {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
         {'bar': 1, 'baz': 6, 'bin': -1, 'foo': 3},
         {'bar': 0, 'baz': 7, 'bin': -1, 'foo': 4}])

by_bar = foos.bar.sortby(reverse=True).groupby()
baz = by_bar.baz
(baz == baz.np().max()).bin = 13

assert (by_bar.aslist() ==
        [[{'bar': 1, 'baz': 6, 'bin': 13, 'foo': 1},
          {'bar': 1, 'baz': 6, 'bin': 13, 'foo': 3}],
         [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
          {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
          {'bar': 0, 'baz': 7, 'bin': 13, 'foo': 4}]])

assert (str(foos.pd()) ==
        '   bar  baz  bin  foo\n'
        '0    1    6   13    1\n'
        '1    1    6   13    3\n'
        '2    0    3   -1    0\n'
        '3    0    5   -1    2\n'
        '4    0    7   13    4')

assert (str(foos.pd(index='foo')) ==
        '     bar  baz  bin\n'
        'foo               \n'
        '1      1    6   13\n'
        '3      1    6   13\n'
        '0      0    3   -1\n'
        '2      0    5   -1\n'
        '4      0    7   13')

assert (by_bar.pd_().pstr().aslist() ==
        ['   bar  baz  bin  foo\n'
         '0    1    6   13    1\n'
         '1    1    6   13    3',

         '   bar  baz  bin  foo\n'
         '0    0    3   -1    0\n'
         '1    0    5   -1    2\n'
         '2    0    7   13    4'])
```
Note the use of `pd_()` on the grouped [`plist`](./pstar_plist.md). This allows you to get a separate `pandas.DataFrame` for
each group in your [`plist`](./pstar_plist.md), and then do normal `DataFrame` manipulations with them individually.
If you want a `pandas.GroupBy` object, you should convert the [`plist`](./pstar_plist.md) to a `DataFrame` first, and then
call `DataFrame.groupby`. Also see `plist.remix` for alternative ways of converting [`plist`](./pstar_plist.md)s to
`DataFrame`s.

**Args:**

>    **`*args`**: Positional arguments passed to `pandas.DataFrame.from_records`.

>    **`**kwargs`**: Keyword arguments passed to `pandas.DataFrame.from_records`.

**Returns:**

>    A `pandas.DataFrame` object constructed from `self`.



## [Source](../pstar/pstar.py#L3468-L3537)