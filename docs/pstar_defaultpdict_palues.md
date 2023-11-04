# [`pstar`](./pstar.md).[`defaultpdict`](./pstar_defaultpdict.md).`palues(self)`

Equivalent to `self.values()`, but returns a [`plist`](./pstar_plist.md) with values sorted as in `self.peys()`.

**Examples:**
```python
pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
assert (pd.palues().aslist() ==
        [2.0, 'three', 1])
```

The [`plist`](./pstar_plist.md) returned is rooted at a corresponding [`plist`](./pstar_plist.md) of `KeyValue` `namedtuple`s,
allowing easy recovery of an equivalent [`pdict`](./pstar_pdict.md), possibly after modifications to the
values:
```python
pd_str = (pd.palues().pstr() + ' foo').pdict()
assert (pd_str ==
        dict(foo='1 foo', bar='2.0 foo', baz='three foo'))
```

**Returns:**

>    [`plist`](./pstar_plist.md) of values from `self`, in the same order given by `self.peys()`.
>    The `root()` of the [`plist`](./pstar_plist.md) is `KeyValue` `namedtuple`s from `self`.



## [Source](../pstar/pstar.py#L784-L808)