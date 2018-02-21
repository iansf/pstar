# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`__setattr__(self, name, val)`

Sets an attribute on a [`plist`](/docs/pstar_plist.md) or its elements to `val`.

This delegates almost entirely to the elements of `self`, allowing natural
assignments of attributes.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])

# Assignment to an existing attribute:
foos.foo += 1
assert (foos.foo.aslist() ==
        [1, 2, 3])

# Scalar assignment to a new attribute:
foos.baz = -1
assert (foos.baz.aslist() ==
        [-1, -1, -1])

# plist assignment to an attribute:
foos.baz *= foos.foo + foos.bar
assert (foos.baz.aslist() ==
        [-1, -3, -3])
```

All of the same things work naturally on a grouped [`plist`](/docs/pstar_plist.md) as well:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()

# Assignment to an existing attribute:
by_bar.foo += 1
assert (by_bar.foo.aslist() ==
        [[1, 3], [2]])

# Scalar assignment to a new attribute:
by_bar.baz = -1
assert (by_bar.baz.aslist() ==
        [[-1, -1], [-1]])

# plist assignment to an attribute:
by_bar.baz *= by_bar.foo + by_bar.bar
assert (by_bar.baz.aslist() ==
        [[-1, -3], [-3]])
```

**Args:**

>    **`name`**: Name of the attribute to set.

>    **`val`**: Value to set the attribute to. If `val` is a [`plist`](/docs/pstar_plist.md) and its length
>         matches `len(self)`, the elements of `val` are set on the elements of
>         `self`. Otherwise, the elements of `self` are all set to `val`.

**Returns:**

>    `self`, in order to allow chaining through `plist.__setattr__(name, val)`.



