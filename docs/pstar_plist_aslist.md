# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`aslist(self)`

Recursively convert all nested [`plist`](./pstar_plist.md)s from `self` to `list`s, inclusive.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()
assert (by_bar.apply(type).aslist() == [plist, plist])
assert ([type(x) for x in by_bar.aslist()] == [list, list])
```

**Returns:**

>    `list` with the same structure and contents as `self`.



## [Source](../pstar/pstar.py#L3354-L3373)