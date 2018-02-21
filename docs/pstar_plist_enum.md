# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`enum(self)`

Wrap the current [`plist`](./pstar_plist.md) values in tuples where the first item is the index.

**Examples:**
```python
pl = plist['a', 'b', 'c']
assert (pl.enum().aslist() ==
        [(0, 'a'), (1, 'b'), (2, 'c')])

foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()
assert (by_bar.foo.enum_().aslist() ==
        [[(0, 0), (1, 2)], [(0, 1)]])
```

**Returns:**

>    [`plist`](./pstar_plist.md) of `(i, x)` pairs from calling `enumerate` on `self`.



## [Source](../pstar/pstar.py#L4062-L4081)