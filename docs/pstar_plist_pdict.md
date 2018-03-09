# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pdict(self, *args, **kwargs)`

Convert `self` to a [`pdict`](./pstar_pdict.md) if there is a natural mapping of keys to values in `self`.

If `self is self.root()`, attempts to treat the contents of `self` as key-value pairs in order
to create the [`pdict`](./pstar_pdict.md) (i.e., `[(key, value), (key, value), ...]`). If that fails, attempts to build
the [`pdict`](./pstar_pdict.md) assuming `self.root()` is a [`plist`](./pstar_plist.md) of `KeyValue` `namedtuple`s, using `self.root().key`
for the keys, and the values in `self` for the values. If that fails, creates a [`pdict`](./pstar_pdict.md) pairing
values from `self.root()` with values from `self`. In that case, if `self is self.root()`, the
[`pdict`](./pstar_pdict.md) will be of the form: `pdict(v1=v1, v2=v2, ...)`, as in the first example below.

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

If you created this [`plist`](./pstar_plist.md) from a [`pdict`](./pstar_pdict.md), but you want to use pairs in `self` to create the
new [`pdict`](./pstar_pdict.md), you will need to [`uproot`](./pstar_plist_uproot.md) first:
```python
pd = pdict(foo=1, bar=2.0, baz=3.3)
pl = pd.palues().apply(lambda x: (str(x), x))
pd2 = pl.pdict()
pd3 = pl.uproot().pdict()
assert (pl.aslist() ==
        [('2.0', 2.0), ('3.3', 3.3), ('1', 1)])
assert (pd2 ==
        dict(foo=('1', 1), bar=('2.0', 2.0), baz=('3.3', 3.3)))
assert (pd3 ==
        {'1': 1, '2.0': 2.0, '3.3': 3.3})
```

**Args:**

>    **`*args`**: Passed to `pdict.update` after the new [`pdict`](./pstar_pdict.md) is created.

>    **`**kwargs`**: Passed to `pdict.update` after the new [`pdict`](./pstar_pdict.md) is created.

**Returns:**

>    New [`pdict`](./pstar_pdict.md) based on the contents of `self`.



## [Source](../pstar/pstar.py#L3536-L3603)