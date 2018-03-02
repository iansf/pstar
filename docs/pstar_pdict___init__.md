# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`__init__(self, *a, **kw)`

Initialize [`pdict`](./pstar_pdict.md).

**Examples:**
```python
pd1 = pdict(foo=1, bar=2.0, baz='three')
pd2 = pdict({'foo': 1, 'bar': 2.0, 'baz': 'three'})
assert (pd1 == pd2)
```

**Args:**

>    **`*a`**: Positional arguments passed through to `dict()`.

>    **`**kw`**: Keyword arguments passed through to `dict()`.

**Returns:**

>    `None`. [`pdict`](./pstar_pdict.md) is initialized.



## [Source](../pstar/pstar.py#L177-L196)