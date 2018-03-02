# [`pstar`](./pstar.md).[`defaultpdict`](./pstar_defaultpdict.md).`__getitem__(self, key)`

Subscript operation. Keys can be any normal `dict` keys or `list`s of such keys.

**Examples:**
```python
pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
assert (pd['foo'] == pd.foo == 1)
assert (pd[['foo', 'bar', 'baz']].aslist() == [1, 2.0, 'three'])
```

When indexing with a `list`, the returned [`plist`](./pstar_plist.md) is rooted at a [`plist`](./pstar_plist.md) of
`KeyValue` `namedtuple`s, making it easy to recover the keys that gave the values, and
allows the [`plist`](./pstar_plist.md) to be turned back into a corresponding [`pdict`](./pstar_pdict.md):
```python
assert (pd[['foo', 'baz']].root().aslist() ==
        [('foo', 1), ('baz', 'three')])
assert (pd[['foo', 'baz']].pdict() ==
        dict(foo=1, baz='three'))
```

**Args:**

>    **`key`**: Any `hash`able object, or a `list` of `hash`able objects.

**Returns:**

>    Either the value held at `key`, or a [`plist`](./pstar_plist.md) of values held at each key in the `list`
>    of keys, when called with a `list` of keys.



## [Source](../pstar/pstar.py#L629-L660)