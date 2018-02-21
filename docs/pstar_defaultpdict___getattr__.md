# [`pstar`](./pstar.md).[`defaultpdict`](./pstar_defaultpdict.md).`__getattr__(self, name)`

Override `getattr`. If `name` starts with '_', attempts to find that attribute on `self`. Otherwise, looks for a field of that name in `self`.

**Examples:**
```python
pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
assert (pd.foo == 1)
assert (pd.__module__.startswith('pstar'))
```

**Args:**

>    **`name`**: A field name or property name on `self`.

**Returns:**

>    Value at `self.<name>` or `self[name]`.



## [Source](../pstar/pstar.py#L506-L525)