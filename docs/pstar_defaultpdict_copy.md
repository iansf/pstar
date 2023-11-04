# [`pstar`](./pstar.md).[`defaultpdict`](./pstar_defaultpdict.md).`copy(self)`

Copy `self` to new [`defaultpdict`](./pstar_defaultpdict.md). Performs a shallow copy.

**Examples:**
```python
pd1 = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
pd2 = pd1.copy()
assert (pd2 == pd1)
assert (pd2 is not pd1)
```

**Returns:**

>    A [`defaultpdict`](./pstar_defaultpdict.md) that is a shallow copy of `self`.



## [Source](../pstar/pstar.py#L746-L761)