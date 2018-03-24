# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__getslice__(self, i, j)`

Delegates to [`__getitem__`](./pstar_plist___getitem__.md) whenever possible. For compatibility with python 2.7.

Avoid using `__getslice__` whenever possible in python 2.7, as the bytecode compiler
assumes that the slice is for the given object on the stack, and modifies negative
indices relative to that object's length. In [`plist`](./pstar_plist.md)s and other dynamic apis like
`numpy`, that assumption can cause undetectable and unrecoverable errors.

To avoid the errors caused by this api in python 2.7, simply use three argument
slices instead of two; e.g., `plist[::1]`.

**Examples:**

The following examples are safe uses of slicing with [`plist`](./pstar_plist.md)s:
```python
pl = plist['abc', 'def', 'ghi']
assert (pl[:2:1].aslist() ==
        ['abc', 'def'])
assert (pl._[:2:1].aslist() ==
        ['ab', 'de', 'gh'])
```

The following example will log a warning -- even though it appears to work, the
underlying bytecode is incorrect:
```python
assert (pl._[:2].aslist() ==
        ['ab', 'de', 'gh'])
# Logs:
#   qj: <pstar> __getslice__: WARNING! <1711>: (multiline log follows)
#   Slicing of inner plist elements with negative indices in python 2.7 does not work, and the error cannot be detected or corrected!
#   Instead of slicing with one or two arguments: `plist._[-2:]`, use the three argument slice: `plist._[-2::1]`.
#   This avoids the broken code path in the python compiler.
```

**Args:**
>    i, j: Beginning and ending indices of `slice`.

**Returns:**

>    [`plist`](./pstar_plist.md) slice of `self`.



## [Source](../pstar/pstar.py#L2225-L2278)