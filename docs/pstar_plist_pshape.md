# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pshape(self)`

Returns a [`plist`](./pstar_plist.md) of the same structure as `self`, filled with leaf lengths.

**Examples:**

`pshape` returns a plist of the same structure as `self`:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pshape().aslist() ==
        [3])

foo_by_bar = foo.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'bar': 0, 'foo': 0},
          {'bar': 0, 'foo': 2}],
         [{'bar': 1, 'foo': 1}]])
assert (foo_by_bar.pshape().aslist() ==
        [[2], [1]])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pshape().aslist() ==
        [[[1], [1]], [[1]]])

filtered = foo_by_bar_foo.bar == 0
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



## [Source](../pstar/pstar.py#L4719-L4768)