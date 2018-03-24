# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`zip(self, *others)`

Zips `self` with `others`, recursively.

**Examples:**
```python
pl1 = plist['a', 'b', 'c']
pl2 = plist[1, 2, 3]
pl3 = plist['nother', 'ig', 'odebase']
assert (pl2.zip(pl1, pl3).aslist() ==
        [(1, 'a', 'nother'), (2, 'b', 'ig'), (3, 'c', 'odebase')])

foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()
assert (by_bar.bar.zip(by_bar.foo).aslist() ==
        [[(0, 0), (0, 2)], [(1, 1)]])
```

**Args:**

>    **`*others`**: `iterable`s that have the same length as `self`.

**Returns:**

>    New [`plist`](./pstar_plist.md) with the same structure as `self`.

**Raises:**
>    `ValueError` if `self` and each `iterable` in `others` don't all have the same length at
>    level `zip` is initially called at.



## [Source](../pstar/pstar.py#L4630-L4666)