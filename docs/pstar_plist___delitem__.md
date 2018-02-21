# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`__delitem__(self, key)`

Deletes items of `self` using a variety of indexing styles.

**Examples:**

Indexing into the [`plist`](/docs/pstar_plist.md) itself:
```python
# Basic scalar indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos[0]
assert (foos.aslist() ==
        [dict(foo=1, bar=1), dict(foo=2, bar=0)])

# plist slice indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos[:2]
assert (foos.aslist() ==
        [dict(foo=2, bar=0)])

# plist int list indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos[[0, 2]]
assert (foos.aslist() ==
        [dict(foo=1, bar=1)])
```

Indexing into the elements of the [`plist`](/docs/pstar_plist.md):
```python
# Basic scalar indexing:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos['foo']
assert (foos.aslist() ==
        [dict(bar=0), dict(bar=1), dict(bar=0)])

# tuple indexing
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos[('foo', 'bar')]
assert (foos.aslist() ==
        [dict(), dict(), dict()])

# list indexing
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos[['foo', 'bar', 'bar']]
assert (foos.aslist() ==
        [dict(bar=0), dict(foo=1), dict(foo=2)])
```

Indexing into the elementes of the [`plist`](/docs/pstar_plist.md) when the elements are indexed by
`int`s, `slice`s, or other means that confict with [`plist`](/docs/pstar_plist.md) indexing:
```python
# Basic scalar indexing:
pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
del pl._[0]
assert (pl.aslist() ==
        [[2, 3], [5, 6], [8, 9]])

# slice indexing (note the use of the 3-argument version of slicing):
pl = plist[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
del pl._[:2:1]
assert (pl.aslist() ==
        [[3], [6], [9]])
```

**Args:**

>    **`key`**: The key to index by.
>         `key` can be applied to `self` directly as:
>           A `list` of `int`s: Deletes from `self` using those `int`s as indices.
>           A `slice`: Deletes from `self` based on the `slice`.
>           An `int`: Deletes the value at that index.
>         `key` can be applied to elements of `self` individually:
>           A generic `list`:
>            Deletes from the elements of `self` using the elements of `key`
>            in order on the elements of `self`.
>           A `tuple` when the elements of `self` can be indexed by `tuple`:
>            Deletes from the elements of `self` by applying that `tuple` to each
>            element of `self`.
>           A `tuple`, otherwise:
>            Deletes from the elements of `self` where each element gets each
>            element in the `key` `tuple` deleted. E.g., `del foo[('bar', 'baz')]`
>            deletes all `'bar'` and `'baz'` keys from each element of `foo`.
>           Anything else:
>            Deletes `key` from each of its elements.

**Returns:**

>    `self`, in order to allow chaining through `plist.__delitem__(key)`.

**Raises:**

>    **`TypeError`**: If `key` fails to be applied directly to `self` and fails to be
>               applied to its elements individually.



