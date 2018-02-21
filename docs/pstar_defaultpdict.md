# [`pstar`](/docs/pstar.md).`defaultpdict(defaultdict)`

`defaultdict` subclass where everything is automatically a property.

**Examples:**

Use with dot notation or subscript notation:
```python
  p = defaultpdict()
  p.foo = 1
  assert (p['foo'] == p.foo == 1)
```

Set the desired default constructor as normal to avoid having to construct
individual values:
```python
  p = defaultpdict(int)
  assert (p.foo == 0)
```

`list` subscripts also work and return a [`plist`](/docs/pstar_plist.md) of the corresponding keys:
```python
  p = defaultpdict(foo=1, bar=2)
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

Setting with a `list` subscript also works, using a single element or a matching
`list` for the values:
```python
  p = defaultpdict()
  p[['foo', 'bar']] = 1
  assert (p[['foo', 'bar']].aslist() == [1, 1])
  p[['foo', 'bar']] = [1, 2]
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

`defaultpdict.update()` returns `self`, rather than `None`, to support chaining:
```python
  p = defaultpdict(foo=1, bar=2)
  p.update(bar=3).baz = 4
  assert (p.bar == 3)
  assert ('baz' in p.keys())
```

Nested `defaultpdict`s make nice lightweight objects:
```python
  p = defaultpdict(lambda: defaultpdict(list))
  p.foo = 1
  p.stats.bar.append(2)
  assert (p['foo'] == 1)
  assert (p.stats.bar == [2])
```

## Children:

### [`pstar.defaultpdict.__getattr__(self, name)`](/docs/pstar_defaultpdict___getattr__.md)

Override `getattr`. If `name` starts with '_', attempts to find that attribute on `self`. Otherwise, looks for a field of that name in `self`.

### [`pstar.defaultpdict.__getitem__(self, key)`](/docs/pstar_defaultpdict___getitem__.md)

Subscript operation. Keys can be any normal `dict` keys or `list`s of such keys.

### [`pstar.defaultpdict.__init__(self, *a, **kw)`](/docs/pstar_defaultpdict___init__.md)

Initialize [`defaultpdict`](/docs/pstar_defaultpdict.md).

### [`pstar.defaultpdict.__setattr__(self, name, value)`](/docs/pstar_defaultpdict___setattr__.md)

Attribute assignment operation. Forwards to subscript assignment.

### [`pstar.defaultpdict.__setitem__(self, key, value)`](/docs/pstar_defaultpdict___setitem__.md)

Subscript assignment operation. Keys and values can be scalars or `list`s.

### [`pstar.defaultpdict.__str__(self)`](/docs/pstar_defaultpdict___str__.md)

Readable string representation of `self`.

### [`pstar.defaultpdict.copy(self)`](/docs/pstar_defaultpdict_copy.md)

Copy `self` to new [`defaultpdict`](/docs/pstar_defaultpdict.md). Performs a shallow copy.

### [`pstar.defaultpdict.palues(self)`](/docs/pstar_defaultpdict_palues.md)

Equivalent to `self.values()`, but returns a [`plist`](/docs/pstar_plist.md) with values sorted as in `self.peys()`.

### [`pstar.defaultpdict.peys(self)`](/docs/pstar_defaultpdict_peys.md)

Get `self.keys()` as a sorted [`plist`](/docs/pstar_plist.md).

### [`pstar.defaultpdict.pitems(self)`](/docs/pstar_defaultpdict_pitems.md)

Equivalent to `self.items()`, but returns a [`plist`](/docs/pstar_plist.md) with items sorted as in `self.peys()`.

### [`pstar.defaultpdict.qj(self, *a, **kw)`](/docs/pstar_defaultpdict_qj.md)

Call the [`qj`](/docs/pstar_pdict_qj.md) logging function with `self` as the value to be logged. All other arguments are passed through to [`qj`](/docs/pstar_pdict_qj.md).

### [`pstar.defaultpdict.rekey(self, map_or_fn=None, inplace=False, **kw)`](/docs/pstar_defaultpdict_rekey.md)

Change the keys of `self` or a copy while keeping the same values.

### [`pstar.defaultpdict.update(self, *a, **kw)`](/docs/pstar_defaultpdict_update.md)

Update `self`. **Returns `self` to allow chaining.**

