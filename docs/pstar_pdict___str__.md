# [`pstar`](./pstar.md).[`pdict`](./pstar_pdict.md).`__str__(self)`

Readable string representation of `self`.

**Examples:**
```python
pd = pdict(foo=1, bar=2.0, baz='three')
assert (str(pd) ==
        "{'bar': 2.0, 'baz': 'three', 'foo': 1}")
```

**Returns:**

>    If the keys in `self` are sortable, returns a string with key/value pairs
>    sorted by key. Otherwise, returns a normal `dict.__str__`
>    representation.



## [Source](../pstar/pstar.py#L267-L288)