# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pset(self)`

Converts the elements of self into pset objects.

Useful for creating `set`s from grouped [`plist`](./pstar_plist.md)s.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.pitems().pset().aslist() ==
        [{('foo', 0), ('bar', 0)}, {('foo', 1), ('bar', 1)}, {('foo', 2), ('bar', 0)}])

by_bar = foos.bar.groupby()
assert (by_bar.foo.pset().aslist() ==
        [{0, 2}, {1}])
```

**Returns:**

>    New [`plist`](./pstar_plist.md) of [`pset`](./pstar_pset.md)s for each value in `self`.



## [Source](../pstar/pstar.py#L3606-L3626)