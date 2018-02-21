# [`pstar`](./pstar.md).[`defaultpdict`](./pstar_defaultpdict.md).`update(self, *a, **kw)`

Update `self`. **Returns `self` to allow chaining.**

**Examples:**
```python
pd = defaultpdict(int)
assert (pd.update(foo=1, bar=2.0).foo == 1)
assert (pd.bar == 2.0)
assert (pd.update({'baz': 'three'}).baz == 'three')
```

**Args:**

>    **`*a`**: Positional args passed to `defaultdict.update`.

>    **`**kw`**: Keyword args passed to `defaultdict.update`.

**Returns:**

>    `self` to allow chaining.



## [Source](../pstar/pstar.py#L641-L661)