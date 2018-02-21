# [`pstar`](./pstar.md).`pdict(dict)`

`dict` subclass where everything is automatically a property.

**Examples:**

Use with dot notation or subscript notation:
```python
  p = pdict()
  p.foo = 1
  assert (p['foo'] == p.foo == 1)
```

`list` subscripts also work and return a [`plist`](./pstar_plist.md) of the corresponding keys:
```python
  p = pdict(foo=1, bar=2)
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

Setting with a `list` subscript also works, using a single element or a matching
`list` for the values:
```python
  p = pdict()
  p[['foo', 'bar']] = 1
  assert (p[['foo', 'bar']].aslist() == [1, 1])
  p[['foo', 'bar']] = [1, 2]
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

`pdict.update()` returns `self`, rather than `None`, to support chaining:
```python
  p = pdict(foo=1, bar=2)
  p.update(bar=3).baz = 4
  assert (p.bar == 3)
  assert ('baz' in p.keys())
```

## Children:

### [`pstar.pdict.__getitem__(self, key)`](./pstar_pdict___getitem__.md)

Subscript operation. Keys can be any normal `dict` keys or `list`s of such keys.

### [`pstar.pdict.__init__(self, *a, **kw)`](./pstar_pdict___init__.md)

Initialize [`pdict`](./pstar_pdict.md).

### [`pstar.pdict.__setitem__(self, key, value)`](./pstar_pdict___setitem__.md)

Subscript assignment operation. Keys and values can be scalars or `list`s.

### [`pstar.pdict.__str__(self)`](./pstar_pdict___str__.md)

Readable string representation of `self`.

### [`pstar.pdict.copy(self)`](./pstar_pdict_copy.md)

Copy `self` to new [`defaultpdict`](./pstar_defaultpdict.md). Performs a shallow copy.

### [`pstar.pdict.palues(self)`](./pstar_pdict_palues.md)

Equivalent to `self.values()`, but returns a [`plist`](./pstar_plist.md) with values sorted as in `self.peys()`.

### [`pstar.pdict.peys(self)`](./pstar_pdict_peys.md)

Get `self.keys()` as a sorted [`plist`](./pstar_plist.md).

### [`pstar.pdict.pitems(self)`](./pstar_pdict_pitems.md)

Equivalent to `self.items()`, but returns a [`plist`](./pstar_plist.md) with items sorted as in `self.peys()`.

### [`pstar.pdict.qj(self, *a, **kw)`](./pstar_pdict_qj.md)

Call the [`qj`](./pstar_defaultpdict_qj.md) logging function with `self` as the value to be logged. All other arguments are passed through to [`qj`](./pstar_defaultpdict_qj.md).

### [`pstar.pdict.rekey(self, map_or_fn=None, inplace=False, **kw)`](./pstar_pdict_rekey.md)

Change the keys of `self` or a copy while keeping the same values.

### [`pstar.pdict.update(self, *a, **kw)`](./pstar_pdict_update.md)

Update `self`. **Returns `self` to allow chaining.**

## [Source](../pstar/pstar.py#L79-L418)