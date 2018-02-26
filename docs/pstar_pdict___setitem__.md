# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`__setitem__(self, key, value)`

Subscript assignment operation. Keys and values can be scalars or `list`s.

**Examples:**

[`pdict`](./pstar_pdict.md) assignment works normally for any `hash`able `key`:
```python
pd = pdict()
pd['foo'] = 1
assert (pd.foo == pd['foo'] == 1)
```

[`pdict`](./pstar_pdict.md) assignment can also work with a `list` of `hash`able `key`s:
```python
pd[['bar', 'baz']] = plist[2.0, 'three']
assert (pd.bar == pd['bar'] == 2.0)
assert (pd.baz == pd['baz'] == 'three')
```

**Args:**

>    **`key`**: Any `hash`able object, or a `list` of `hash`able objects.

>    **`value`**: Any value, or a [`plist`](./pstar_plist.md) of values that matches the shape of `key`, if it
>           is a `list`.

**Returns:**

>    `self`, to allow chaining with direct calls to `pdict.__setitem__`.



## [Source](../pstar/pstar.py#L232-L266)