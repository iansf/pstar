# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`pstructure(self)`

Returns a `list` of the number of elements in each layer of `self`.

Gives a snapshot view of the structure of `self`. The length of the returned
list is the depth of `self`. Each value in the list is the result of calling
`self.plen(r)`, where `r` ranges from 0 to `self.pdepth()`. `plen(r)` gives
the sum of the lengths of all plists at layer `r`.

**Examples:**
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pstructure().aslist() ==
        [3])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pstructure().aslist() ==
        [2, 3, 3])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pstructure().aslist() ==
        [2, 3, 2])
```

**Returns:**

>    A `list` (not a [`plist`](/docs/pstar_plist.md)) of `self.pdepth()` integers, where each integer is
>    the number of elements in all [`plist`](/docs/pstar_plist.md)s at that layer, 0-indexed according to
>    depth.



