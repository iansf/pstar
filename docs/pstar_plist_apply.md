# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`apply(self, func, *args, **kwargs)`

Apply an arbitrary function to elements of self, forwarding arguments.

Any arguments passed to `apply` that are [`plist`](./pstar_plist.md)s and have the same
length as `self` will be passed one-at-a-time to `func` with each
element of `self`. Otherwise, arguments are passed in unmodified.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.foo.apply('foo: {}'.format).aslist() ==
        ['foo: 0', 'foo: 1', 'foo: 2'])
assert (foos.foo.apply('foo: {}, bar: {}'.format, foos.bar).aslist() ==
        ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])
assert (foos.foo.apply('foo: {}, bar: {bar}'.format, bar=foos.bar).aslist() ==
        ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])

# The same as above, but in parallel:
assert (foos.foo.apply('foo: {}, bar: {}'.format, foos.bar, psplit=1).aslist() ==
        ['foo: 0, bar: 0', 'foo: 1, bar: 1', 'foo: 2, bar: 0'])

by_bar = foos.bar.groupby()
assert (by_bar.foo.apply('bar: {bar} => {}'.format, bar=foos.bar.puniq()).aslist() ==
        ['bar: 0 => [0, 2]', 'bar: 1 => [1]'])
assert (by_bar.foo.apply_('bar: {bar} => {}'.format, bar=by_bar.bar).aslist() ==
        [['bar: 0 => 0', 'bar: 0 => 2'], ['bar: 1 => 1']])
```

Using `paslist` and `psplat`:
```python
foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

by_bar_baz = foos.bar.groupby().baz.groupby()

by_bar_baz_apply_paslist = by_bar_baz.foo.apply(
    lambda x, *a, **kw: {'{x}: {a} ({kw})'.format(x=x, a=a, kw=kw)}, by_bar_baz.baz, bar=by_bar_baz.bar, paslist=True)
by_bar_baz_apply_paslist_psplat = by_bar_baz.foo.apply(
    lambda *a, **kw: {'{a} ({kw})'.format(a=a, kw=kw)}, by_bar_baz.baz, bar=by_bar_baz.bar, paslist=True, psplat=True)

assert (by_bar_baz_apply_paslist.aslist() ==
        [["[[0], [2], [4]]: ([[3], [1], [2]],) ({'bar': [[0], [0], [0]]})"],
         ["[[1, 3]]: ([[6, 6]],) ({'bar': [[1, 1]]})"]])
assert (by_bar_baz_apply_paslist_psplat.aslist() ==
        [["([0], [2], [4], [[3], [1], [2]]) ({'bar': [[0], [0], [0]]})"],
         ["([1, 3], [[6, 6]]) ({'bar': [[1, 1]]})"]])
```

**Args:**

>    **`func`**: `callable`, `list` of `callable`s, or string name of method in [`plist`](./pstar_plist.md).

>    **`*args`**: Arguments to pass to `func`.

>    **`**kwargs`**: Keyword arguments to pass to `func`, after extracting:

>    **`paslist`**: Boolean (default `False`). If `True`, converts
>             elements of `self` to `list` using `plist.aslist()`
>             before passing them to `func`, and reconverts the
>             result of each call to a [`plist`](./pstar_plist.md). Note that this does
>             not guarantee that the returned [`plist`](./pstar_plist.md) has the same
>             shape as `self`, as `plist.aslist()` recursively
>             converts all contained [`plist`](./pstar_plist.md)s to `list`s, but `func`
>             might return any arbitrary result, so the same
>             conversion cannot be inverted automatically.

>    **`psplat`**: Boolean (default `False`). If `True`, expands the
>            arguments provided by `self` with the `*` operator
>            (sometimes called the 'splat' operator).

>    **`psplit`**: Integer (default `0`). If greater than `0`, `func` is
>            applied in parallel. If `psplit` is `1`, the number of
>            parallel executions is equal to the length of `self`.
>            Otherwise, `psplit` is the number of parallel executions.

**Returns:**

>    [`plist`](./pstar_plist.md) resulting from applying `func` to each element of `self`.



## [Source](../pstar/pstar.py#L3466-L3584)