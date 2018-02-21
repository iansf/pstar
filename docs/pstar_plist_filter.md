# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`filter(self, func=<type 'bool'>, *args, **kwargs)`

Filter `self` by an arbitrary function on elements of `self`, forwarding arguments.

`filter` always returns the root of the filtered [`plist`](./pstar_plist.md).

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.foo.filter().aslist() ==
        [dict(foo=1, bar=1), dict(foo=2, bar=0)])
assert (foos.foo.filter(lambda x: x < 2).aslist() ==
        [dict(foo=0, bar=0), dict(foo=1, bar=1)])

(foos.bar == 0).bin = 'zero'
(foos.bar == 1).bin = 1
assert (foos.bin.filter(isinstance, str).aslist() ==
        [{'bar': 0, 'bin': 'zero', 'foo': 0}, {'bar': 0, 'bin': 'zero', 'foo': 2}])
```

**Args:**

>    **`func`**: callable. Defaults to `bool`. Return value will be cast to `bool`.

>    **`*args`**: Arguments to pass to `func`.

>    **`**kwargs`**: Keyword arguments to pass to `func`, after extracting the same arguments as `plist.apply`.

**Returns:**

>    [`plist`](./pstar_plist.md) resulting from filtering out elements of `self` for whom `func` evaluated to a `False` value.



## [Source](../pstar/pstar.py#L3746-L3774)