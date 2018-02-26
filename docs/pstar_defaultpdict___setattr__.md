# [`pstar`](./pstar.md).[`defaultpdict`](./pstar_defaultpdict.md).`__setattr__(self, name, value)`

Attribute assignment operation. Forwards to subscript assignment.

Permits [`pdict`](./pstar_pdict.md)-style field assignment.

**Examples:**
```python
pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
pd.floo = 4.0
assert (pd.floo == pd['floo'] == 4.0)
```

**Args:**

>    **`name`**: Any `hash`able value or list of `hash`able values, as in [`__setitem__`](./pstar_defaultpdict___setitem__.md),
>          but generally just a valid identifier string provided by the compiler.

>    **`value`**: Any value, or [`plist`](./pstar_plist.md) of values of the same length as the corresponding list in
>           `name`.

**Returns:**

>    `self` to allow chaining through direct calls to `defaultpdict.__setattr__(...)`.



## [Source](../pstar/pstar.py#L608-L631)