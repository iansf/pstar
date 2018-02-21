# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`update(self, *a, **kw)`

Update `self`. **Returns `self` to allow chaining.**

**Examples:**
```python
pd = pdict()
assert (pd.update(foo=1, bar=2.0).foo == 1)
assert (pd.bar == 2.0)
assert (pd.update({'baz': 'three'}).baz == 'three')
```

**Args:**

>    **`*a`**: Positional args passed to `dict.update`.

>    **`**kw`**: Keyword args pass to `dict.update`.

**Returns:**

>    `self` to allow chaining.



## [Source](../pstar/pstar.py#L227-L247)