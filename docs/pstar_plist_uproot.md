# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`uproot(self)`

Sets the root to `self` so future `root()` calls return this [`plist`](./pstar_plist.md).

**Examples:**

In some cases it is better reset the root. For example, after applying
a number of operations to a [`plist`](./pstar_plist.md) to get the data into the desired form,
resetting the root to `self` often makes sense, as future filtering
should not return the original data:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
(foos.bar == 0).baz = 6
(foos.bar == 1).baz = foos.foo * 2
floos = foos.rekey(dict(foo='floo'))
assert (floos.root() is foos)
assert (floos.peys()[0].aslist() ==
        ['bar', 'baz', 'floo'])
assert ((floos.floo < 2).aslist() ==
        [dict(foo=0, bar=0, baz=6), dict(foo=1, bar=1, baz=2)])
floos = floos.uproot()
assert ((floos.floo < 2).aslist() ==
        [dict(floo=0, bar=0, baz=6), dict(floo=1, bar=1, baz=2)])
```

See `plist.root` for more details.

**Returns:**

>    `self`.



## [Source](../pstar/pstar.py#L3290-L3321)