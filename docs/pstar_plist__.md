# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`_(self)`

Causes the next call to `self` to be performed as deep as possible in the [`plist`](./pstar_plist.md).

This is a convenience method primarily for easy subscripting of the values of
a [`plist`](./pstar_plist.md).

**Examples:**
```python
pl = plist([np.arange(10) for _ in range(3)])
assert (pl._[2].aslist() ==
        [2, 2, 2])
import operator as op
assert (pl._[2:4:1].apply(op.eq,
                          [np.array([2, 3]), np.array([2, 3]), np.array([2, 3])])
                   .apply(np.all).aslist() ==
        [True, True, True])
```

It can be used to call any method on the values of a [`plist`](./pstar_plist.md) as well:
```python
pl = plist([['foo'], ['bar']])
pl._.append('baz')
assert (pl.apply(type).aslist() ==
        [list, list])
assert (pl.aslist() ==
        [['foo', 'baz'], ['bar', 'baz']])
```

**Returns:**

>    `self`, but in a state such that the next access to a property or method of
>    `self` occurs at the maximum depth.



## [Source](../pstar/pstar.py#L2829-L2863)