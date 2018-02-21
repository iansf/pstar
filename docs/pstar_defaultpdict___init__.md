# [`pstar`](/docs/pstar.md).[`defaultpdict`](/docs/pstar_defaultpdict.md).`__init__(self, *a, **kw)`

Initialize [`defaultpdict`](/docs/pstar_defaultpdict.md).

**Examples:**
```python
pd = defaultpdict(int)
assert (pd.foo == 0)
pd.bar += 10
assert (pd.bar == 10)

pd = defaultpdict(lambda: defaultpdict(list))
pd.foo.bar = 20
assert (pd == dict(foo=dict(bar=20)))
pd.stats.bar.append(2)
assert (pd.stats.bar == [2])
```

**Args:**

>    **`*a`**: Positional arguments passed through to `defaultdict()`.

>    **`**kw`**: Keyword arguments pass through to `defaultdict()`.

**Returns:**

>    `None`. [`defaultpdict`](/docs/pstar_defaultpdict.md) is initialized.



