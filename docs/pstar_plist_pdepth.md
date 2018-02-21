# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pdepth(self, s=False)`

Returns a [`plist`](./pstar_plist.md) of the recursive depth of each leaf element, from 0.

**Examples:**

`pdepth` returns a plist of the same plist structure as self:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pdepth().aslist() ==
        [0])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pdepth().aslist() ==
        [[[2], [2]], [[2]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pdepth().aslist() ==
        [[[2], [2]], [[]]])
```

Since the depth values are always equal or empty in well-formed plists, it
is sometimes more convenient to get the depth as a scalar value. Pass a True
value to the first parameter (`s` for 'scalar'):
```python
assert (foo.pdepth(s=1) == 0)
assert (foo_by_bar_foo.pdepth(1) == 2)
assert (filtered.pdepth(True) == 2)
```

**Args:**

>    **`s`**: Boolean that controls whether a scalar is returned (when `True`) or a
>       plist of the same structure as self (when `False`, the default).

**Returns:**

>    plist whose elements are the recursive depth of the leaf children, or a
>    scalar representing the maximum depth encountered in self if `s` is
>    `True`.



## [Source](../pstar/pstar.py#L4582-L4642)