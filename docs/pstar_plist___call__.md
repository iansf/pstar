# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`__call__(self, *args, **kwargs)`

Call each element of self, possibly recusively.

Any arguments passed to `__call__` that are [`plist`](./pstar_plist.md)s and have the same
length as `self` will be passed one-at-a-time to the each of the `callable`s
in `self`. Otherwise, arguments are passed in unmodified.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])

# A plist of callables, one for each pdict:
foos_peys = foos.peys
assert (foos_peys.all(callable))

# The actual call to plist.__call__ (separated out for demonstration):
assert (foos_peys().aslist() ==
        [['bar', 'foo'], ['bar', 'foo'], ['bar', 'foo']])

# Of course, you would normally do the above like this, which is the same:
assert (foos.peys().aslist() ==
        [['bar', 'foo'], ['bar', 'foo'], ['bar', 'foo']])

by_bar = foos.bar.groupby()

# There's rarely any need to pass pepth, as the call gets routed to the
# correct object by default in almost all situations, even with grouped
# plists:
assert (by_bar.peys().aslist() ==
        [[['bar', 'foo'], ['bar', 'foo']], [['bar', 'foo']]])
```

All argument calling conventions are possible:
```python
pl = plist['foo {}', 'bar {}', 'baz {}']

# Basic positional argument passing:
assert (pl.format(0).aslist() ==
        ['foo 0', 'bar 0', 'baz 0'])

# Passing a plist in a positional argument:
assert (pl.format(pl._[:3:1]).aslist() ==
        ['foo foo', 'bar bar', 'baz baz'])

# Basic keyword argument passing:
pl = pl.replace('{}', '{foo}')
assert (pl.format(foo=0).aslist() ==
        ['foo 0', 'bar 0', 'baz 0'])

# Passing a plist as a keyword argument:
assert (pl.format(foo=pl._[:3:1]).aslist() ==
        ['foo foo', 'bar bar', 'baz baz'])
```

They work the same way on grouped plists:
```python
pl = plist['foo {}', 'bar {}', 'baz {}']
by = pl._[0].groupby()  # Group by first character.
assert (by.aslist() ==
        [['foo {}'], ['bar {}', 'baz {}']])

# Basic positional argument passing:
assert (by.format(0).aslist() ==
        [['foo 0'], ['bar 0', 'baz 0']])

# Passing a plist in a positional argument:
assert (by.format(by._[:3:1]).aslist() ==
        [['foo foo'], ['bar bar', 'baz baz']])

# Basic keyword argument passing:
by = by.replace('{}', '{foo}')
assert (by.format(foo=0).aslist() ==
        [['foo 0'], ['bar 0', 'baz 0']])

# Passing a plist as a keyword argument:
assert (by.format(foo=by._[:3:1]).aslist() ==
        [['foo foo'], ['bar bar', 'baz baz']])
```

**Args:**

>    **`*args`**: Arguments to pass to elements of `self`.

>    **`**kwargs`**: Keyword arguments to pass to elements of `self`, after extracting:

>    **`pepth`**: Integer (default `0`). If greater than `0`, calls occur at that
>           depth in the [`plist`](./pstar_plist.md). Equivalent to appending '_'s at the end of the
>           name of the attribute (see `plist.__getattribute__`). If less than
>           `0`, calls occur as deep in the [`plist`](./pstar_plist.md) as possible. Equivalent to
>           calling `plist._` before calling the attribute.

>    **`psplit`**: Integer (default `0`). If greater than `0`, calls to elements of
>            `self` are applied in parallel. If `psplit` is `1`, the number of
>            parallel executions is equal to the length of `self`.
>            Otherwise, `psplit` is the number of parallel executions.

>    **`call_pepth`**: *Private -- do not pass.* Internal state variable for tracking
>                how deep the call stack is in [`plist`](./pstar_plist.md) code, for use with
>                internal methods that need access to the original caller's
>                stack frame.

**Returns:**

>    New [`plist`](./pstar_plist.md) resulting from calling element of `self`.



## [Source](../pstar/pstar.py#L2322-L2453)