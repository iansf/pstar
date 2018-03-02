# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`puniq(self)`

Returns a new [`plist`](./pstar_plist.md) with only a single element of each value in `self`.

**Examples:**

`puniq` reduces the values of the groups of self using an equality check:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
reduced = foos.bar.puniq()
assert (reduced.aslist() ==
        [0, 1])
assert (reduced.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

Grouped plists
```python
foo_by_bar = foos.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
reduced = foo_by_bar.bar.puniq()
assert (reduced.aslist() ==
        [[0], [1]])
assert (reduced.root().aslist() ==
        [[{'foo': 0, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
```

The equality check respects the subgroups of self:
```python
by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
reduced_no_effect = by_bar_foo.bar.puniq()
assert (reduced_no_effect.aslist() ==
        [[[0], [0]], [[1]]])
assert (reduced_no_effect.root().aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
```

As with `plist.groupby`, `puniq` relies on the values being hashable.
If, for some reason, you need to reduce by a non-hashable value, you should
convert it to a hashable representation first, for example using
`plist.pstr()` or `plist.apply(id)`:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=0, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 0, 'bar': 0}])
try:
  reduced_crash = foos.puniq()  # CRASHES!
except Exception as e:
  assert (isinstance(e, TypeError))
reduced_pstr = foos.pstr().puniq()
assert (reduced_pstr.aslist() ==
        ["{'bar': 0, 'foo': 0}",
         "{'bar': 1, 'foo': 1}"])
assert (reduced_pstr.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
reduced_id = foos.apply(id).puniq()
assert (reduced_id.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 0, 'bar': 0}])
```
In the last case, since each of the elements of `foo` are unique pdicts,
reducing by `plist.apply(id)` has no useful effect, but if there had been
any duplicates in the elements of `foo`, they would have been removed.

**Returns:**

>    New [`plist`](./pstar_plist.md) with a new [`root`](./pstar_plist_root.md) where there is only one example of each value
>    in each sublist. The corresponding root element is the first element in
>    `self.root()` that has that value.



## [Source](../pstar/pstar.py#L4723-L4832)