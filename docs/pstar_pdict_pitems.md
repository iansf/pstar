# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`pitems(self)`

Equivalent to `self.items()`, but returns a [`plist`](./pstar_plist.md) with items sorted as in `self.peys()`.

**Examples:**
```python
pd = pdict(foo=1, bar=2.0, baz='three')
assert (pd.pitems().aslist() ==
        [('bar', 2.0), ('baz', 'three'), ('foo', 1)])
assert (pd.pitems().key.aslist() ==
        pd.peys().aslist())
assert (pd.pitems().value.aslist() ==
        pd.palues().aslist())
```
In the example above, note that the items are `KeyValue` `namedtuple`s,
so the first element can be accessed with `.key` and the second with `.value`.

**Returns:**

>    [`plist`](./pstar_plist.md) of items from `self`, in the same order given by `self.peys()`.



## [Source](../pstar/pstar.py#L377-L397)