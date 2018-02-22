# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`aspdict(self)`

Convert `self` to a [`pdict`](./pstar_pdict.md) if there is a natural mapping of keys to values in `self`.

Recursively creates a [`pdict`](./pstar_pdict.md) from `self`. Experimental, likely to change.

**Examples:**
```python
pl = plist['foo', 'bar', 'baz']
assert (pl.pdict() ==
        dict(foo='foo', bar='bar', baz='baz'))
assert (pl.replace('a', '').replace('o', '').pdict() ==
        dict(foo='f', bar='br', baz='bz'))

foos = plist([pdict(foo=0, bar=0, baz=3), pdict(foo=1, bar=1, baz=2), pdict(foo=2, bar=0, baz=1)])
by_bar = foos.bar.groupby()
assert (by_bar.bar.ungroup().puniq().zip(by_bar).aspdict() ==
        {0: [{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 1, 'foo': 2}],
         1: [{'bar': 1, 'baz': 2, 'foo': 1}]})
assert ([type(x) for x in by_bar.astuple()] == [tuple, tuple])
```

**Returns:**

>    New [`pdict`](./pstar_pdict.md) based on the contents of `self`.



## [Source](../pstar/pstar.py#L3058-L3088)