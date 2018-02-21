# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__getattribute__(self, name)`

Returns a plist of the attribute for self, or for each element.

If `name` exists as an attribute of plist, that attribute is returned.
Otherwise, removes trailing underscores from `name` (apart from those
normally part of a `__*__` name), and uses the count of underscores to
indicate how deep into the plist `name` should be searched for. Attempts
to find the modified `name` on plist first, and then looks for `name` on
each element of self.

When attempting to find `name` on the elements of self, first it checks
if the elements all have `name` as an attribute. If so, it returns that
attribute (`[getattr(x, name) for x in self]`). Otherwise, it attempts to
return `name` as an index of each element (`[x[name] for x in self]`).

**Examples:**

A [`plist`](./pstar_plist.md) of `list`s has `append` methods at two levels -- the [`plist`](./pstar_plist.md)
and the contained `list`s. To chose `list.append` them, you can add
an '_' to the method name:
```python
pl = plist[[1, 2, 3], [4, 5, 6]]
pl.append([7, 8, 9])
assert (pl.aslist() ==
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
pl.append_(10)
assert (pl.aslist() ==
        [[1, 2, 3, 10], [4, 5, 6, 10], [7, 8, 9, 10]])
```

Grouped [`plist`](./pstar_plist.md)s also have methods that you might want to call at different
depths. Adding an '_' for each layer of the [`plist`](./pstar_plist.md) you want to skip
allows you to control which depth the method is executed at:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()

assert (by_bar.foo.apply(str).aslist() ==
        ['[0, 2]', '[1]'])
assert (by_bar.foo.apply_(str).aslist() ==
        [['0', '2'], ['1']])

# (Note that it is better to use `plist.pstr` to get string representation of
# leaf elements:)
assert (by_bar.foo.pstr().aslist() ==
        [['0', '2'], ['1']])
```

**Args:**

>    **`name`**: Name of the attribute.

**Returns:**

>    Bound [`plist`](./pstar_plist.md) attribute, or [`plist`](./pstar_plist.md) of bound attributes of the elements
>    of `self`.

**Raises:**

>    **`AttributeError`**: If `name` is is a reserved member of the elements of `self`.

>    **`AttributeError`**: If `name` is not found on `self` or the elements of `self`.



## [Source](../pstar/pstar.py#L1523-L1612)