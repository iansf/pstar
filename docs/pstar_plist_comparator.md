# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`comparator(self, other, return_inds=False)`

[`plist`](./pstar_plist.md) comparison operator. **Comparisons filter plists.**

**IMPORTANT:** [`plist`](./pstar_plist.md) comparisons all filter the [`plist`](./pstar_plist.md) and return a new
[`plist`](./pstar_plist.md), rather than a truth value.

`comparator` is not callable directly from [`plist`](./pstar_plist.md). It implements the various
python comparison operations: `==`, `<`, `>`, etc. The comparison operators
can be called directly with their corresponding 'magic' functions,
`plist.__eq__`, `plist.__lt__`, `plist.__gt__`, etc., but are generally just
called implicitly.

**Examples:**
[`plist`](./pstar_plist.md) comparators can filter on leaf values:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
zero_bars = foos.bar == 0
assert (zero_bars.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
nonzero_bars = foos.bar != 0
assert (nonzero_bars.aslist() ==
        [{'foo': 1, 'bar': 1}])
```

They can also filter on other plists so long as the structures are
compatible:
```python
assert ((foos == zero_bars).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
assert ((foos.foo > foos.bar).aslist() ==
        [{'foo': 2, 'bar': 0}])
```

The same is true when comparing against lists with compatible structure:
```python
assert ((foos.foo == [0, 1, 3]).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

This all generalizes naturally to plists that have been grouped:
```python
by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
nonzero_by_bar_foo = by_bar_foo.bar > 0
assert (nonzero_by_bar_foo.aslist() ==
        [[[],
          []],
         [[{'bar': 1, 'foo': 1}]]])
zero_by_bar_foo = by_bar_foo.foo != nonzero_by_bar_foo.foo
assert (zero_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[]]])
assert ((by_bar_foo.foo == [[[0], [3]], [[1]]]).aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          []],
         [[{'foo': 1, 'bar': 1}]]])
```

Lists with incompatible structure are compared to `self` one-at-a-time,
resulting in set-like filtering where the two sets are merged with an 'or':
```python

assert ((foos.foo == [0, 1, 3, 4]).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])

assert ((by_bar_foo.foo == [0, 1, 3, 4]).aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          []],
         [[{'foo': 1, 'bar': 1}]]])
```

When comparing against an empty list, `==` always returns an empty list, but
all other comparisons return `self`:
```python
assert ((foos.foo == []).aslist() == [])
assert ((foos.foo < []).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert ((by_bar_foo == nonzero_by_bar_foo).aslist() ==
        [[[],
          []],
         [[{'foo': 1, 'bar': 1}]]])
assert ((by_bar_foo.foo > nonzero_by_bar_foo.foo).aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[]]])
```

Note that `plist.nonempty` can be used to remove empty internal [`plist`](./pstar_plist.md)s
after filtering a grouped [`plist`](./pstar_plist.md):
```python
assert ((by_bar_foo == nonzero_by_bar_foo).nonempty(-1).aslist() ==
        [[[{'foo': 1, 'bar': 1}]]])
```

**Args:**

>    **`other`**: Object to compare against.

>    **`return_inds`**: Optional bool. When `True`, causes the comparison to return
>                 the plist indices of the matching items. When `False`
>                 (the default), causes the comparison to return a plist of the
>                 matching values.

**Returns:**

>    A new plist, filtered from `self` and `other` according to the operation
>    provided to `_build_comparator`, if `return_inds` is `False`. Otherwise,
>    returns the corresponding indices into self.



## [Source](../pstar/pstar.py#L1128-L1281)