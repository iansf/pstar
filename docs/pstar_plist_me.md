# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`me(self, name_or_plist='me', call_pepth=0)`

Sets the current plist as a variable available in the caller's context.

`me` is a convenience method to naturally enable long chaining to prepare
the data in the [`plist`](./pstar_plist.md) for a future call to [`apply`](./pstar_plist_apply.md) or some other call. It
attempts to add the current [`plist`](./pstar_plist.md) to the caller's context, either as a
local variable, or as a global (module-level) variable. Because it modifies
the caller's frame, it is not recommended for production code, but can be
useful in jupyter notebooks and colabs during exploration of datasets.

**Examples:**

Using `me` with a local variable requires that the variable already exist in
the local context, and that it be a [`plist`](./pstar_plist.md):
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos.baz = 3 * foos.foo + foos.bar
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0, 'baz': 0},
         {'foo': 1, 'bar': 1, 'baz': 4},
         {'foo': 2, 'bar': 0, 'baz': 6}])
def new_context():
  me = plist()
  foos.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.bar)
new_context()
```

The same can work with a name of your choice:
```python
def new_context():
  baz = plist()
  foos.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
new_context()
```

You can pass the [`plist`](./pstar_plist.md) you want to use instead:
```python
def new_context():
  me2 = plist()
  foos.bar.groupby().baz.sortby_().groupby().me(me2).foo.plt().plot(me2.foo + 1)
new_context()
```

If there isn't a local variable of that name, `me()` will put the [`plist`](./pstar_plist.md) into
the caller's `globals()` `dict` under the requested name. The following both
work if there are no local or global variables named `me` or `baz`:
```python
def new_context():
  foos.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.baz)
  foos.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
  del globals()['me']
  del globals()['baz']
new_context()
```

**Args:**

>    **`name_or_plist`**: String naming a variable in the caller's context or the
>                   global (module-level) context, or an existing plist. In
>                   both cases, the variable will be overwritten with a plist
>                   that is a shallow copy of `self`. Defaults to `'me'`.

>    **`call_pepth`**: Do not pass. Used by `plist.__call__` to keep track of how
>                many stack frames occur between the caller and `me()`.

**Returns:**

>    `self`, permitting continued chaining.

**Raises:**

>    **`ValueError`**: If `name_or_plist` is a string, and that name appears in the
>                caller's local variables, but does not evaluate to a [`plist`](./pstar_plist.md).

>    **`ValueError`**: If something other than a string or a [`plist`](./pstar_plist.md) is passed to
>                `name_or_plist`.



## [Source](../pstar/pstar.py#L5441-L5544)