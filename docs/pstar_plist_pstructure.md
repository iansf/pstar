# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pstructure(self)`

Returns a `list` of the number of elements in each layer of `self`.

Gives a snapshot view of the structure of `self`. The length of the returned
list is the depth of `self`. Each value in the list is the result of calling
`self.plen(r)`, where `r` ranges from 0 to `self.pdepth()`. `plen(r)` gives
the sum of the lengths of all plists at layer `r`.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foos.pstructure().aslist() ==
        [3])

by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (by_bar_foo.pstructure().aslist() ==
        [2, 3, 3])

filtered = by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pstructure().aslist() ==
        [2, 3, 2])
```

**Returns:**

>    A `list` (not a [`plist`](./pstar_plist.md)) of `self.pdepth()` integers, where each integer is
>    the number of elements in all [`plist`](./pstar_plist.md)s at that layer, 0-indexed according to
>    depth.



## [Source](../pstar/pstar.py#L5147-L5191)