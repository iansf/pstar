# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`logical_op(self, other)`

[`plist`](./pstar_plist.md) logical operation. **Logical operations perform set operations on [`plist`](./pstar_plist.md)s.**

**IMPORTANT:** [`plist`](./pstar_plist.md) logical operations between two [`plist`](./pstar_plist.md)s perform `set` operations
on the two [`plist`](./pstar_plist.md)s. Logical operations between a [`plist`](./pstar_plist.md) and any other type attempts
to perform that operation on the values in the [`plist`](./pstar_plist.md) and `other` itself.

`logical_op` is not callable directly from [`plist`](./pstar_plist.md). It implements the various
python logical operations: `&`, `|`, `^`, etc. The logical operators
can be called directly with their corresponding 'magic' functions,
`plist.__and__`, `plist.__or__`, `plist.__xor__`, etc., but are generally just
called implicitly.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6

assert (((foos.bar == 0) & (foos.baz == 3)).aslist() ==
        [{'baz': 3, 'foo': 0, 'bar': 0}])

assert (((foos.bar == 0) | (foos.baz == 3)).aslist() ==
        [{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}])

assert (((foos.bar == 0) ^ (foos.baz == 3)).aslist() ==
        [{'bar': 0, 'baz': 5, 'foo': 2}])

by_bar = foos.bar.groupby()

assert (((by_bar.bar == 0) & (by_bar.bar == 1)).aslist() ==
        [[], []])
assert (((by_bar.bar == 0) & (by_bar.bar <= 1)).aslist() ==
        [[{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}], []])

assert (((by_bar.baz == 3) | (by_bar.baz == 6)).aslist() ==
        [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
assert (((by_bar.baz == 6) | (by_bar.baz <= 4)).aslist() ==
        [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])

assert (((by_bar.baz == 3) ^ (by_bar.baz == 6)).aslist() ==
        [[{'bar': 0, 'baz': 3, 'foo': 0}], [{'bar': 1, 'baz': 6, 'foo': 1}]])
assert (((by_bar.baz == 6) ^ (by_bar.bar <= 4)).aslist() ==
        [[{'bar': 0, 'baz': 3, 'foo': 0}, {'bar': 0, 'baz': 5, 'foo': 2}], []])
```

Logical operations can be applied element-wise if `other` is not a [`plist`](./pstar_plist.md):
```python
assert ((foos.baz & 1).aslist() ==
        [1, 0, 1])
assert ((by_bar.baz | 1).aslist() ==
        [[3, 5], [7]])
assert ((1 ^ by_bar.baz).aslist() ==
        [[2, 4], [7]])
```

**Args:**

>    **`other`**: Object to perform the logical operation with.

**Returns:**

>    New [`plist`](./pstar_plist.md), merging `self` and `other` according to the operation provided
>    to `_build_logical_op`.



## [Source](../pstar/pstar.py#L1034-L1116)