# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`reduce(self, func, *args, **kwargs)`

Apply a function repeatedly to its own result, returning a plist of length at most 1.

`reduce` can be initialized either by using the `initial_value` keyword argument,
or by the first value in `args`, if anything is passed to `args`, or from the first value
in `self`, if the other options are not present.

**Examples:**

This is an example of passing `initial_value` as the first value in `args`:
```python
s = 'foo bar was a baz of bin'
pl = plist['foo', 'bar', 'baz', 'bin']
reduced = pl.reduce(lambda s, x, y: qj(s).replace(x, y), s, pl._[::-1])
# Logs:
#   qj: <pstar> reduce: s <3451>: foo bar was a baz of bin
#   qj: <pstar> reduce: s <3451>: oof bar was a baz of bin
#   qj: <pstar> reduce: s <3451>: oof rab was a baz of bin
#   qj: <pstar> reduce: s <3451>: oof rab was a zab of bin
assert (reduced.aslist() ==
        ['oof rab was a zab of nib'])
assert (reduced.root().aslist() ==
        ['foo bar was a baz of bin'])
assert (reduced.root().root() is pl)
```

The same thing, but using the `initial_value` keyword argument:
```python
reduced = pl.reduce(lambda s, x, y: qj(s).replace(x, y), pl._[::-1], initial_value=s)
assert (reduced.aslist() ==
        ['oof rab was a zab of nib'])
assert (reduced.root().aslist() ==
        ['foo bar was a baz of bin'])
assert (reduced.root().root() is pl)
```

Using the first value in `self` for the initial value:
```python
pl = plist[1, 2, 3, 4, 5]
reduced = pl.reduce(lambda x, y, z: (x + y) * z, z=pl[::-1])
assert (reduced.aslist() ==
        [466])
```
Any additional `args` or `kwargs` values will be passed through to `func` at each call,
in parallel to values of `self`. Note that [`plist`](./pstar_plist.md) arguments of the same length as `self`
get passed through starting at the 0th element, and going until there are no more elements
of `self`. If no value was passed for `initial_value`, this means that any additional
arguments will only use `n-1` values. For example, in the code above, `z` ranges from 5 to
2, producing the following computation:
```python
assert ((((((1 + 2) * 5 + 3) * 4 + 4) * 3 + 5) * 2) ==
        466)
```

When `self` is a grouped [`plist`](./pstar_plist.md), `pepth` determines which groups are reduced over:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0), pdict(foo=3, bar=1), pdict(foo=4, bar=0)])
(foos.bar == 0).baz = 3 + (foos.bar == 0).foo
(foos.bar == 1).baz = 6
foos.bin = (foos.baz + foos.bar) * foos.foo
by_bar_baz_bin = foos.bar.groupby().baz.groupby().bin.groupby()
assert (by_bar_baz_bin.aslist() ==
        [[[[{'bar': 0, 'baz': 3, 'bin': 0, 'foo': 0}]],
          [[{'bar': 0, 'baz': 5, 'bin': 10, 'foo': 2}]],
          [[{'bar': 0, 'baz': 7, 'bin': 28, 'foo': 4}]]],
         [[[{'bar': 1, 'baz': 6, 'bin': 7, 'foo': 1}],
           [{'bar': 1, 'baz': 6, 'bin': 21, 'foo': 3}]]]])

import operator as op
assert (by_bar_baz_bin.foo.reduce(op.add, initial_value=0).aslist() ==
        [10])
assert (by_bar_baz_bin.foo.reduce_(op.add, initial_value=0).aslist() ==
        [[6], [4]])
assert (by_bar_baz_bin.foo.reduce__(op.add, initial_value=0).aslist() ==
        [[[0], [2], [4]], [[4]]])
assert (by_bar_baz_bin.foo.reduce___(op.add, initial_value=0).aslist() ==
        [[[[0]], [[2]], [[4]]], [[[1], [3]]]])
```
Notice that the deepest reduction actually returns a reconstruction of the input plist,
`by_bar_baz_bin.foo`, because at that level every element is in its own plist.

You can also pass a list of functions to apply. The first function is applied to the
broadest layer of the plist. Any additional layers consume a function. If the functions
run out before the last layer, all the deeper layers get the last function from the list.
If the layers run out before the functions do, deeper functions are not used in the
reduction.
```python
assert (by_bar_baz_bin.foo.reduce_(op.add, 0).reduce(op.mul, 1).aslist() ==
        [24])
assert (by_bar_baz_bin.foo.reduce([op.mul, op.add], 0).aslist() ==
        [24])
```
Note how `op.add` is applied to the deepest layers in both examples, and `op.mul` is only applied
to the outermost plist, performing `6 * 4`.

You can also set `initial_value` using a plist of the same structure:
```python
assert (by_bar_baz_bin.foo.reduce(op.add, by_bar_baz_bin.baz).aslist() ==
        [37])
assert (by_bar_baz_bin.foo.reduce([op.mul, op.add, op.mul, op.add], initial_value=by_bar_baz_bin.baz).aslist() ==
        [1323])
```

Note that `reduce` does not currently provide a good mechanism for using a function of more than two arguments
while reducing a deep plist, as that would require a reduction operation to be provided for each additional argument.
Therefore, attempting to reduce a deep plist with a multiargument function is likely to crash or give unexpected
results, and is not recommended.

**Args:**

>    **`func`**: function to call. Must take at least two positional arguments of the same type as `self`,
>          and return a value of that type.

>    **`*args`**: Additional arguments to pass to func at each step. If `initial_value` is not in
>           `kwargs`, then the first value in `args` is used as `initial_value`.

>    **`**kwargs`**: Additional kwargs to pass to `func`. If `initial_value` is passed, it is
>              removed from `kwargs` and used as the first argument passed to `func` on
>              the first call.



## [Source](../pstar/pstar.py#L4153-L4313)