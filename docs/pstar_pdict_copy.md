# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`copy(self)`

Copy `self` to new [`defaultpdict`](./pstar_defaultpdict.md). Performs a shallow copy.

**Examples:**
```python
pd1 = pdict(foo=1, bar=2.0, baz='three')
pd2 = pd1.copy()
assert (pd2 == pd1)
assert (pd2 is not pd1)
```

**Returns:**

>    A [`pdict`](./pstar_pdict.md) that is a shallow copy of `self`.



## [Source](../pstar/pstar.py#L248-L263)