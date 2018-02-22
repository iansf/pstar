# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`any(self, *args, **kwargs)`

Returns `self` if `args[0]` evaluates to `True` for any elements of `self`.

Shortcuts if `args[0]` ever evaluates to `True`.
If `args` are not passed, the function evaluated is `bool`.

Useful as an implicit `if` condition in chaining, but can be used explicitly
in `if` statements as well.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.any(isinstance, pdict).aslist() ==
        [pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.foo.any(lambda x: x < 0).aslist() == [])
```

`any` does not recurse into grouped [`plist`](./pstar_plist.md)s, so you must specify the
desired level of evaluation:
```python
by_bar = foos.bar.groupby()
assert (by_bar.foo.any_(lambda x: x > 1).aslist() ==
        [[0, 2], []])
assert (by_bar.foo.any_(lambda x: x > 1).nonempty().root().aslist() ==
        [[{'bar': 0, 'foo': 0}, {'bar': 0, 'foo': 2}]])
```

**Args:**

>    **`*args`**: Optional. If present, the first entry must be a function to evaluate.
>           All other args are passed through to that function. If absent, the
>           function is set to `bool`.

>    **`**kwargs`**: Passed through to the function specified in `*args`.

**Returns:**

>    `self` or an empty [`plist`](./pstar_plist.md) (which evaluates to `False`).



## [Source](../pstar/pstar.py#L3505-L3550)