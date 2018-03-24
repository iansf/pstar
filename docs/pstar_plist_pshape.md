# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pshape(self)`

Returns a [`plist`](./pstar_plist.md) of the same structure as `self`, filled with leaf lengths.

**Examples:**

`pshape` returns a plist of the same structure as `self`:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foos.pshape().aslist() ==
        [3])

foo_by_bar = foos.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'bar': 0, 'foo': 0},
          {'bar': 0, 'foo': 2}],
         [{'bar': 1, 'foo': 1}]])
assert (foo_by_bar.pshape().aslist() ==
        [[2], [1]])

by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (by_bar_foo.pshape().aslist() ==
        [[[1], [1]], [[1]]])

filtered = by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pshape().aslist() ==
        [[[1], [1]], [[]]])
```

**Returns:**

>    New [`plist`](./pstar_plist.md) of the same structure as `self`, where each leaf [`plist`](./pstar_plist.md) has a
>    single element, which is the length of the corresponding leaf [`plist`](./pstar_plist.md) in
>    `self`.



## [Source](../pstar/pstar.py#L5097-L5146)