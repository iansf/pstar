# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pand(self, name='__plist_and_var__', call_pepth=0)`

Stores `self` into a [`plist`](./pstar_plist.md) of `tuple`s that gets extended with each call.

`pand` is meant to facilitate building up `tuple`s of values to be sent as
a single block to a chained call to [`apply`](./pstar_plist_apply.md), or as `*args` when calling
`plist.apply(psplat=True)`. The name is `pand` to evoke conjunction: the
caller wants a [`plist`](./pstar_plist.md) with this *and* this *and* this.

`pand` stores a variable in the caller's frame that isn't visible to the
caller, but is visible to future calls to `pand` due to how `locals()`
works.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foos.baz = 3 * foos.foo + foos.bar
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0, 'baz': 0},
         {'foo': 1, 'bar': 1, 'baz': 4},
         {'foo': 2, 'bar': 0, 'baz': 6}])
def new_context():
  assert (foos.bar.groupby().baz.groupby().foo.pand().root().bar.pand().ungroup()
              .apply_(qj, '(foo, bar)') ==
          [[[(0, 0)],
            [(2, 0)]],
           [[(1, 1)]]])
new_context()
# Logs:
#   qj: <pstar> apply: (foo, bar) <1249>: (0, 0)
#   qj: <pstar> apply: (foo, bar) <1249>: (2, 0)
#   qj: <pstar> apply: (foo, bar) <1249>: (1, 1)
```

The same construction can be used with methods that expect the arguments
individually, requiring the `tuple` to be expanded:
```python
def new_context():
  (foos.bar.groupby().baz.groupby().foo.pand().root().bar.pstr().pand()
       .ungroup().apply_(qj, psplat=True, b=0))
new_context()
# Logs:
#   qj: <pstar> apply: (foo, bar) <2876>: (0, 0)
#   qj: <pstar> apply: (foo, bar) <2876>: (2, 0)
#   qj: <pstar> apply: (foo, bar) <2876>: (1, 1)
#   qj: <pstar> apply: (0, 0) <2876>: (0, 0)
#   qj: <pstar> apply: (2, 0) <2876>: (2, 0)
#   qj: <pstar> apply: (1, 1) <2876>: (1, 1)
```

Building multiple `tuple`s in the same context requires passing `name` to keep
them separate:
```python
def new_context():
  me = plist()
  assert (foos.bar.groupby().baz.groupby().me().foo.pand().root().bar.pand().ungroup()
              .apply_(qj,
                      me.foo.pand('strs').root().bar.pand('strs').ungroup().pstr()) ==
          [[(0, 0),
            (2, 0)],
           [(1, 1)]])
new_context()
# Logs:
#   qj: <pstar> apply: (0, 0) <1249>: (0, 0)
#   qj: <pstar> apply: (2, 0) <1249>: (2, 0)
#   qj: <pstar> apply: (1, 1) <1249>: (1, 1)
```
Note that the construction above is hard to understand, and probably
shouldn't be used.

**Args:**

>    **`name`**: String naming an available variable in the caller's context. Should
>          only be passed if the calling frame needs to create multiple
>          different `tuple`s. Defaults to '__plist_and_var__'. If a variable of
>          the same name exists in the caller's context, `pand` will fail to
>          write to it.

>    **`call_pepth`**: Do not pass. Used by `plist.__call__` to keep track of how
>                many stack frames occur between the caller and `pand()`.

**Returns:**

>    The current [`plist`](./pstar_plist.md) of `tuple`s, with `self` added.

**Raises:**

>    **`ValueError`**: If the variable named by `name` is already present in the
>                caller's frame and is not a [`plist`](./pstar_plist.md), or has different `pshape()`
>                than `self`.



## [Source](../pstar/pstar.py#L5419-L5532)