# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__dir__(self)`

Allow natural tab-completion on `self` and its contents.

**Examples:**
```python
pl = plist['a', 'b', 'c']
assert ('capitalize' in dir(pl))
assert ('groupby' in dir(pl))

foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert ('foo' in dir(foos))
assert ('groupby' in dir(foos))
assert ('foo' in dir(foos.bar.groupby()))
```

**Returns:**

>    Combined [`plist`](./pstar_plist.md) of methods and properties available on `self` and its contents.



## [Source](../pstar/pstar.py#L3084-L3107)