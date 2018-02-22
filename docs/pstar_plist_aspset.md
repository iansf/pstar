# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`aspset(self)`

Recursively convert all nested [`plist`](./pstar_plist.md)s from `self` to [`pset`](./pstar_pset.md)s, inclusive.

All values must be hashable for the conversion to succeed.

**Examples:**
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.bar.aspset() == pset([0, 1]))
by_bar = foo.bar.groupby()
assert (by_bar.bar.apply(type).aslist() == [plist, plist])
assert ([type(x) for x in by_bar.bar.aspset()] == [pset, pset])
```

**Returns:**

>    [`pset`](./pstar_pset.md) with the same structure and contents as `self`.



## [Source](../pstar/pstar.py#L3036-L3058)