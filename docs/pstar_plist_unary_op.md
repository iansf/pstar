# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`unary_op(self)`

[`plist`](./pstar_plist.md) unary operation; applied element-wise to `self`.

`unary_op` is not callable directly from [`plist`](./pstar_plist.md). It implements the various
python unary operations: `-`, `~`, `abs`, etc. The unary operators
can be called directly with their corresponding 'magic' functions,
`plist.__neg__`, `plist.__invert__`, `plist.__abs__`, etc., but are generally just
called implicitly.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6

assert ((-foos.foo).aslist() ==
        [0, -1, -2])
assert ((~foos.foo).aslist() ==
        [-1, -2, -3])

by_bar = foos.bar.groupby()

assert ((-by_bar.foo).aslist() ==
        [[0, -2], [-1]])
assert ((~by_bar.foo).aslist() ==
        [[-1, -3], [-2]])
```

**Returns:**

>    A new [`plist`](./pstar_plist.md), where each element of `self` had the operation passed to
>    `_build_unary_op` applied to it.



## [Source](../pstar/pstar.py#L1498-L1531)