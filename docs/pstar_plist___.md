# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__(self)`

Causes the next call to `self` to be performed on the innermost [`plist`](./pstar_plist.md).

This is a convenience method primarily for easy subscripting of the innermost [`plist`](./pstar_plist.md).

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()
assert (by_bar.__[0].aslist() ==
        [{'bar': 0, 'foo': 0}, {'bar': 1, 'foo': 1}])
# This makes slicing the innermost plist easy as well, but note the three-argument slice:
assert (by_bar.__[:1:].aslist() ==
        [[{'bar': 0, 'foo': 0}], [{'bar': 1, 'foo': 1}]])
```

It can be used to call any method on the values of a [`plist`](./pstar_plist.md) as well:
```python
pl = plist * [['foo'], ['bar']]
pl.__.append('baz')
assert (pl.apply(type).aslist() ==
        [plist, plist])
assert (pl.aslist() ==
        [['foo', 'baz'], ['bar', 'baz']])
```

Compare the use of `__` with the use of [`_`](./pstar_plist__.md), which will work on the leaf values if they
support the property being accessed:
```python
# Get the first two characters from the strings in the innermost plist.
assert (pl._[:2:].aslist() ==
        [['fo', 'ba'], ['ba', 'ba']])
# Get the first two elements from the innermost plist (which in this case is the entire plist).
assert (pl.__[:2:].aslist() ==
        [['foo', 'baz'], ['bar', 'baz']])
```

**Returns:**

>    `self`, but in a state such that the next access to a property or method of
>    `self` occurs at the innermost [`plist`](./pstar_plist.md).



## [Source](../pstar/pstar.py#L3178-L3221)