# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pequal(self, other)`

Shortcutting recursive equality function.

`pequal` always returns `True` or `False` rather than a plist. This is a
convenience method for cases when the filtering that happens with `==` is
undesirable or inconvenient.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foos.pequal(foos) == True)

zero_bars = foos.bar == 0
assert (zero_bars.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
assert ((foos == zero_bars).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
assert (foos.pequal(zero_bars) == False)
```

**Args:**

>    **`other`**: Object to check equality against.

**Returns:**

>    True if all elements of self and other are recursively equal.
>    False otherwise.



## [Source](../pstar/pstar.py#L3866-L3912)