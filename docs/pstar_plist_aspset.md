# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`aspset(self)`

Recursively convert all nested [`plist`](/docs/pstar_plist.md)s from `self` to [`pset`](/docs/pstar_plist_pset.md)s, inclusive.

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

>    [`pset`](/docs/pstar_plist_pset.md) with the same structure and contents as `self`.



