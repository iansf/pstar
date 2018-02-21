# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`np(self, *args, **kwargs)`

Converts the elements of `self` to `numpy.array`s, forwarding passed args.

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

assert (foos.foo.wrap().np().sum().aslist() ==
        [10])

by_bar = foos.bar.sortby(reverse=True).groupby()
baz = by_bar.baz
# Filters for the max per group, which includes the two-way tie in the first group.
(baz == baz.np().max()).bin = 13

assert (by_bar.aslist() ==
        [[{'bar': 1, 'baz': 6, 'bin': 13, 'foo': 1},
          {'bar': 1, 'baz': 6, 'bin': 13, 'foo': 3}],
         [{'bar': 0, 'baz': 3, 'bin': -1, 'foo': 0},
          {'bar': 0, 'baz': 5, 'bin': -1, 'foo': 2},
          {'bar': 0, 'baz': 7, 'bin': 13, 'foo': 4}]])

assert ((by_bar.foo.np() * by_bar.baz.np() - by_bar.bin.np()).sum().aslist() ==
        [-2, 27])
```

**Args:**

>    **`*args`**: Positional arguments passed to `np.array`.

>    **`**kwargs`**: Keyword arguments passed to `np.array`.

**Returns:**

>    New [`plist`](./pstar_plist.md) with values from `self` converted to `np.array`s.



## [Source](../pstar/pstar.py#L2919-L2962)