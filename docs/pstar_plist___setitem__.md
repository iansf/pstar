# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__setitem__(self, key, val)`

Sets items of `self` using a variety of indexing styles.

**Examples:**

Indexing into the [`plist`](./pstar_plist.md) itself:
```python
# Basic scalar indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos[0] = 13
assert (foos.aslist() ==
        [13, dict(foo=1, bar=1), dict(foo=2, bar=0)])

# plist slice indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos[:2] = plist[12, 13]
assert (foos.aslist() ==
        [12, 13, dict(foo=2, bar=0)])

# plist int list indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos[[0, 2]] = plist[12, 13]
assert (foos.aslist() ==
        [12, dict(foo=1, bar=1), 13])
```

Indexing into the elements of the [`plist`](./pstar_plist.md):
```python
# Basic scalar indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos['foo'] = plist[4, 5, 6]
assert (foos.aslist() ==
        [dict(foo=4, bar=0), dict(foo=5, bar=1), dict(foo=6, bar=0)])

# list indexing
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos[['foo', 'bar', 'bar']] = plist[4, 5, 6]
assert (foos.aslist() ==
        [dict(foo=4, bar=0), dict(foo=1, bar=5), dict(foo=2, bar=6)])
```

Indexing into the elementes of the [`plist`](./pstar_plist.md) when the elements are indexed by
`int`s, `slice`s, or other means that confict with [`plist`](./pstar_plist.md) indexing:
```python
# Basic scalar indexing:
pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
pl._[0] = 13
assert (pl.aslist() ==
        [[13, 2, 3], [13, 5, 6], [13, 8, 9]])

# slice indexing (note the use of the 3-argument version of slicing):
pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
pl._[:2:1] = pl._[1:3:1]
assert (pl.aslist() ==
        [[2, 3, 3], [5, 6, 6], [8, 9, 9]])

# list indexing:
pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]].np()
pl._[[True, False, True]] = plist[[5, 6], [7, 8], [9, 0]]
assert (pl.apply(list).aslist() ==
        [[5, 2, 6], [7, 5, 8], [9, 8, 0]])
```

**Args:**

>    **`key`**: The key to index by.
>         `key` can be applied to `self` directly as:
>           A `list` of `int`s: Sets items using those `int`s as indices.
>           A `slice`: Sets items based on the `slice`.
>           An `int`: Sets the item at that index.
>         `key` can be applied to elements of `self` individually:
>           A generic `list`:
>            Sets the items of `self` using the elements of `key` in order.
>           A `tuple` when the elements of `self` can be indexed by `tuple`:
>            Sets the elements of `self` using that `tuple` to index into each
>            element.
>           A `tuple`, otherwise:
>            Sets the elements of `self` using each element of the `key`
>            `tuple` on each element. E.g., `foo[('bar', 'baz')] = 1`
>            will set the `bar` and `baz` keys of `foo` to `1`.
>           Anything else:
>            Sets the elements of `self` indexed by `key` to `val`.

>    **`val`**: Value to assign. If `val` is a [`plist`](./pstar_plist.md) and its length matches either
>         `len(self)` (in most cases described above for `key`) or `len(key)`,
>         each element of `val` is applied to each corresponding element of
>         `self` or `self[k]`.

**Returns:**

>    `self`, in order to allow chaining through `plist.__setitem__(key, val)`.

**Raises:**

>    **`TypeError`**: If `key` fails to be applied directly to `self` and fails to be
>               applied to its elements individually.



## [Source](../pstar/pstar.py#L2354-L2487)