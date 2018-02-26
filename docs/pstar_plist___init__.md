# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__init__(self, *args, **kwargs)`

Constructs plist.

**Examples:**
```python
# Empty plists:
pl = plist()
pl = plist([])

# Convenience constructor for list literals:
pl = plist[1, 2, 3]
pl = plist[1,]  # Note the trailing comma, which is required for 1-element lists.

# Initialization from other lists or plists:
pl = plist(['a', 'b', 'c'])
pl = plist(pl)

# Initialization from iterables:
pl = plist(range(5))
pl = plist([i for i in range(5)])
pl = plist((i for i in range(5)))

# Passing root (advanced usage -- not generally necessary):
pl = plist([1, 2, 3], root=plist(['a', 'b', 'c']))
```

**Args:**

>    **`*args`**: Passed directly to `list` constructor.

>    **`**kwargs`**: Keyword arguments passed directly to `list` constructor after
>              exctracting [`root`](./pstar_plist_root.md) if present. [`root`](./pstar_plist_root.md) must be a [`plist`](./pstar_plist.md), and
>              will be used as the root of `self`.

**Returns:**

>    `None`. [`plist`](./pstar_plist.md) is initialized.



## [Source](../pstar/pstar.py#L1921-L1959)