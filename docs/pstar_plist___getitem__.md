# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__getitem__(self, key)`

Returns a new [`plist`](./pstar_plist.md) using a variety of indexing styles.

**Examples:**

Indexing into the [`plist`](./pstar_plist.md) itself:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])

# Basic scalar indexing:
assert (foos[0] ==
        dict(foo=0, bar=0))

# plist slice indexing:
assert (foos[:2].aslist() ==
        [dict(foo=0, bar=0), dict(foo=1, bar=1)])

# plist int list indexing:
assert (foos[[0, 2]].aslist() ==
        [dict(foo=0, bar=0), dict(foo=2, bar=0)])
```

Indexing into the elements of the [`plist`](./pstar_plist.md):
```python
# Basic scalar indexing:
assert (foos['foo'].aslist() ==
        [0, 1, 2])

# tuple indexing
assert (foos[('foo', 'bar')].aslist() ==
        [(0, 0), (1, 1), (2, 0)])

# list indexing
assert (foos[['foo', 'bar', 'bar']].aslist() ==
        [0, 1, 0])
```

Indexing into the elementes of the [`plist`](./pstar_plist.md) when the elements are indexed by
`int`s, `slice`s, or other means that confict with [`plist`](./pstar_plist.md) indexing:
```python
pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# Basic scalar indexing:
assert (pl._[0].aslist() ==
        [1, 4, 7])

# slice indexing (note the use of the 3-argument version of slicing):
assert (pl._[:2:1].aslist() ==
        [[1, 2], [4, 5], [7, 8]])

# list indexing:
pl = pl.np()
assert (pl._[[True, False, True]].apply(list).aslist() ==
        [[1, 3], [4, 6], [7, 9]])
```

**Args:**

>    **`key`**: The key to index by.
>         `key` can be applied to `self` directly as:
>           A `list` of `int`s: Returns a [`plist`](./pstar_plist.md) using those `int`s as indices.
>           A `slice`: Returns a [`plist`](./pstar_plist.md) based on the `slice`.
>           An `int`: Returns the value at that index (may not be a [`plist`](./pstar_plist.md)).
>         `key` can be applied to elements of `self` individually:
>           A generic `list`:
>            Returns a [`plist`](./pstar_plist.md) using the elements of `key` in order on the
>            elements of `self`.
>           A `tuple` when the elements of `self` can be indexed by `tuple`:
>            Returns a [`plist`](./pstar_plist.md) applying that `tuple` to each element of `self`.
>           A `tuple`, otherwise:
>            Returns a [`plist`](./pstar_plist.md) where each element of the new [`plist`](./pstar_plist.md) is a `tuple`
>            of each value in the `key` `tuple` applied to each element of
>            `self`. E.g., `foo[('bar', 'baz')]` might return
>            `plist([(1, 2), (3, 4), ...])`.
>           Anything else:
>            Returns a [`plist`](./pstar_plist.md) of the `key` applied to each of its elements.

**Returns:**

>    A [`plist`](./pstar_plist.md) based on the order of attempting to apply `key` described above.

**Raises:**

>    **`TypeError`**: If `key` fails to be applied directly to `self` and fails to be
>               applied to its elements individually.



## [Source](../pstar/pstar.py#L1845-L1952)