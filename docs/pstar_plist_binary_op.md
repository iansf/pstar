# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`binary_op(self, other)`

[`plist`](./pstar_plist.md) binary operation; applied element-wise to `self`.

`binary_op` is not callable directly from [`plist`](./pstar_plist.md). It implements the various
python binary operations: `+`, `-`, `*`, etc. The binary operators
can be called directly with their corresponding 'magic' functions,
`plist.__add__`, `plist.__sub__`, `plist.__mul__`, etc., but are generally just
called implicitly.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6

assert ((foos.foo + foos.baz).aslist() ==
        [3, 7, 7])
assert ((2 * (foos.foo + 7)).aslist() ==
        [14, 16, 18])

by_bar = foos.bar.groupby()

assert ((by_bar.foo + by_bar.baz).aslist() ==
        [[3, 7], [7]])
assert ((2 * (by_bar.foo + 7)).aslist() ==
        [[14, 18], [16]])
```

The only binary operation that doesn't work as expected is string interpolation:
`'foo: %d' % foos.foo`. This can't work as expected because python handles that
operation in a special manner. However, `+` works on [`plist`](./pstar_plist.md)s of strings, as
does `plist.apply('{}'.format)`:
```python
assert (('foo: ' + foos.foo.pstr() + ' bar: ' + foos.bar.pstr()).aslist() ==
        ['foo: 0 bar: 0', 'foo: 1 bar: 1', 'foo: 2 bar: 0'])
assert (foos.foo.apply('foo: {} bar: {}'.format, foos.bar).aslist() ==
        ['foo: 0 bar: 0', 'foo: 1 bar: 1', 'foo: 2 bar: 0'])

assert (('foo: ' + by_bar.foo.pstr() + ' bar: ' + by_bar.bar.pstr()).aslist() ==
        [['foo: 0 bar: 0', 'foo: 2 bar: 0'], ['foo: 1 bar: 1']])
assert (by_bar.foo.apply('foo: {} bar: {}'.format, by_bar.bar).aslist() ==
        ['foo: [0, 2] bar: [0, 0]', 'foo: [1] bar: [1]'])
assert (by_bar.foo.apply_('foo: {} bar: {}'.format, by_bar.bar).aslist() ==
        [['foo: 0 bar: 0', 'foo: 2 bar: 0'], ['foo: 1 bar: 1']])
```
Note the difference between the final two examples using `apply()` vs. `apply_()` on
grouped [`plist`](./pstar_plist.md)s.

**Args:**

>    **`other`**: Object to perform the binary operation with.

**Returns:**

>    A new plist, where each element of `self` had the operation passed to
>    `_build_binary_op` applied to it and `other`, or the corresponding element
>    of `other`, if the lengths of `self` and `other` match.



## [Source](../pstar/pstar.py#L1389-L1462)