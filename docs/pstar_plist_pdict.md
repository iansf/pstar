# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pdict(self, *args, **kwargs)`

Convert `self` to a [`pdict`](./pstar_pdict.md) if there is a natural mapping of keys to values in `self`.

Attempts to treat the contents of `self` as key-value pairs in order to create the [`pdict`](./pstar_pdict.md).
If that fails, checks if `self.root()` is a [`plist`](./pstar_plist.md) of `KeyValue` `namedtuple`s. If so, uses
`self.root().key` for the keys, and the values in `self` for the values. Otherwise,
attempts to create a [`pdict`](./pstar_pdict.md) pairing values from `self.root()` with values from `self`.

**Examples:**
```python
pl = plist['foo', 'bar', 'baz']
assert (pl.pdict() ==
        dict(foo='foo', bar='bar', baz='baz'))
assert (pl.replace('a', '').replace('o', '').pdict() ==
        dict(foo='f', bar='br', baz='bz'))

pd = pdict(foo=1, bar=2, floo=0)
assert (pd.pitems().pdict() == pd)
assert (pd.palues().pdict() == pd)
assert ((pd.palues() + 2).pdict() ==
        dict(foo=3, bar=4, floo=2))
assert (pd.peys()._[0].pdict(),
        pdict(foo='f', bar='b', floo='f'))

foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.foo.pstr().zip(foos.bar).uproot().pdict() ==
        {'0': 0, '1': 1, '2': 0})

assert (plist[('foo', 1), ('foo', 2)].pdict() ==
        dict(foo=2))
```

**Returns:**

>    New [`pdict`](./pstar_pdict.md) based on the contents of `self`.



## [Source](../pstar/pstar.py#L3231-L3273)