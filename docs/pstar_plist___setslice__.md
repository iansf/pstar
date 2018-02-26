# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__setslice__(self, i, j, sequence)`

Delegates to [`__setitem__`](./pstar_plist___setitem__.md) whenever possible. For compatibility with python 2.7.

Avoid using `__setslice__` whenever possible in python 2.7, as the bytecode compiler
assumes that the slice is for the given object on the stack, and modifies negative
indices relative to that object's length. In [`plist`](./pstar_plist.md)s and other dynamic apis like
`numpy`, that assumption can cause undetectable and unrecoverable errors.

To avoid the errors caused by this api in python 2.7, simply use three argument
slices instead of two; e.g., `plist[::1]`.

**Examples:**

The following examples are safe uses of slicing with [`plist`](./pstar_plist.md)s:
```python
pl = plist['abc', 'def', 'ghi']
pl[:2:1] = plist['dec', 'abf']
assert (pl.aslist() ==
        ['dec', 'abf', 'ghi'])

# Turn strings into mutable lists:
pl = pl.apply(list)
# Change slices of the lists:
pl._[:2:1] = pl._[1:3:1]
# Turn the lists back into strings
pl = pl.apply(''.join)
assert (pl.aslist() ==
        ['ecc', 'bff', 'hii'])
```

The following example will log a warning -- even though it appears to work, the
underlying bytecode is incorrect:
```python
pl = pl.apply(list)
pl._[:2] = plist['ab', 'de', 'gh']
pl = pl.apply(''.join)
assert (pl.aslist() ==
        ['abc', 'def', 'ghi'])
# Logs:
#   qj: <pstar> __setslice__: WARNING! <1711>: (multiline log follows)
#   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
#   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
#   This avoids the broken code path in the python compiler.
```

**Args:**
>    i, j: Beginning and ending indices of `slice`.

>    **`sequence`**: `iterable` object to assign to the slice.

**Returns:**

>    `self`, to permit chaining through direct calls to `plist.__setslice__`.



## [Source](../pstar/pstar.py#L2470-L2534)