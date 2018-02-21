# [`pstar`](/docs/pstar.md).[`defaultpdict`](/docs/pstar_defaultpdict.md).`rekey(self, map_or_fn=None, inplace=False, **kw)`

Change the keys of `self` or a copy while keeping the same values.

Convenience method for renaming keys in a [`defaultpdict`](/docs/pstar_defaultpdict.md). Passing a `dict` mapping
old keys to new keys allows easy selective renaming, as any key not in the
`dict` will be unchanged. Passing a `callable` requires you to return a unique
value for every key in `self`.

**Examples:**
```python
pd = defaultpdict(int).update(foo=1, bar=2.0, baz='three')
assert (pd.rekey(foo='floo') ==
        dict(floo=1, bar=2.0, baz='three'))
assert (pd.foo == 1)  # pd is unmodified by default.
pd.rekey(dict(bar='car'), True)
assert ('bar' not in pd)
assert (pd.car == 2.0)

pd.rekey(lambda k: 'far' if k == 'car' else k, True)
assert ('car' not in pd)
assert (pd.far == 2.0)
```

**Args:**

>    **`map_or_fn`**: `dict` mapping current keys to new keys, or `callable` taking a single
>               argument (the key) and returning a new key, or `None`, in which case
>               `**kw` should map keys to new keys.

>    **`inplace`**: Boolean (default: `False`). If `True`, updates the keys of `self`. If
>             `False`, returns a new [`defaultpdict`](/docs/pstar_defaultpdict.md).

>    **`**kw`**: Additional keys to rekey. Convenience for existing keys that are valid
>          identifiers.

**Returns:**

>    `self` if `inplace` evaluates to `True`, otherwise a new [`defaultpdict`](/docs/pstar_defaultpdict.md). The keys will
>    be changed, but the values will remain the same.

**Raises:**

>    **`ValueError`**: If `map_or_fn` isn't a `dict` or a `callable` or `None`.

>    **`ValueError`**: If `map_or_fn` fails to generate a unique key for every key in `self`.



