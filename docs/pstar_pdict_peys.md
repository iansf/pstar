# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`peys(self)`

Get `self.keys()` as a sorted [`plist`](./pstar_plist.md).

In the common case of a [`pdict`](./pstar_pdict.md) with sortable keys, it is often convenient
to rely on the sort-order of the keys for a variety of operations that would
otherwise require explicit looping.

**Examples:**
```python
pd = pdict(foo=1, bar=2.0, baz='three')
assert (pd.peys().aslist() == ['bar', 'baz', 'foo'])
pd_str = pdict()
pd_str[pd.peys()] = pd.palues().pstr()  # Converts the values to strings.
assert (pd_str ==
        dict(foo='1', bar='2.0', baz='three'))
```

**Returns:**

>    [`plist`](./pstar_plist.md) of keys in sorted order.



## [Source](../pstar/pstar.py#L330-L351)