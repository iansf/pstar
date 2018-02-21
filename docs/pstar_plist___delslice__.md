# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__delslice__(self, i, j)`

Delegates to [`__delitem__`](./pstar_plist___delitem__.md) whenever possible. For compatibility with python 2.7.

Avoid using `__delslice__` whenever possible in python 2.7, as the bytecode compiler
assumes that the slice is for the given object on the stack, and modifies negative
indices relative to that object's length. In [`plist`](./pstar_plist.md)s and other dynamic apis like
`numpy`, that assumption can cause undetectable and unrecoverable errors.

To avoid the errors caused by this api in python 2.7, simply use three argument
slices instead of two; e.g., `plist[::1]`.

**Examples:**

The following examples are safe uses of slicing with [`plist`](./pstar_plist.md)s:
```python
pl = plist['abc', 'def', 'ghi']
del pl[:2:1]
assert (pl.aslist() ==
        ['ghi'])

# Change slices of the lists:
pl = plist['abc', 'def', 'ghi']
# Turn strings into mutable lists:
pl = pl.apply(list)
del pl._[:2:1]
# Turn lists back into strings:
pl = pl.apply(''.join)
assert (pl.aslist() ==
        ['c', 'f', 'i'])
```

The following example will log a warning -- even though it appears to work, the
underlying bytecode is incorrect:
```python
pl = plist['abc', 'def', 'ghi']
# Turn strings into mutable lists:
pl = pl.apply(list)
del pl._[:2]
# Turn lists back into strings:
pl = pl.apply(''.join)
assert (pl.aslist() ==
        ['c', 'f', 'i'])
# Logs:
#   qj: <pstar> __delslice__: WARNING! <1711>: (multiline log follows)
#   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
#   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
#   This avoids the broken code path in the python compiler.
```

**Args:**
>    i, j: Beginning and ending indices of `slice`.

>    **`sequence`**: `iterable` object to assign to the slice.

**Returns:**

>    `self`, to permit chaining through direct calls to `plist.__setslice__`.



## [Source](../pstar/pstar.py#L2250-L2318)