# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`aspset(self)`

Recursively convert all nested [`plist`](./pstar_plist.md)s from `self` to [`pset`](./pstar_pset.md)s, inclusive.

All values must be hashable for the conversion to succeed. Grouped [`plist`](./pstar_plist.md)s
necessarily return [`frozenpset`](./pstar_frozenpset.md)s at all non-root nodes.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.bar.aspset() == pset([0, 1]))
by_bar = foos.bar.groupby()
assert (by_bar.bar.apply(type).aslist() == [plist, plist])
assert (type(by_bar.bar.aspset()) == pset)
assert ([type(x) for x in by_bar.bar.aspset()] == [frozenpset, frozenpset])
```

**Returns:**

>    [`pset`](./pstar_pset.md) with the same structure and contents as `self`.



## [Source](../pstar/pstar.py#L3296-L3323)