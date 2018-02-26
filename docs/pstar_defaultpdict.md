# [`pstar`](./pstar.md).`defaultpdict(defaultdict)`

`defaultdict` subclass where everything is automatically a property.

**Examples:**

Use with dot notation or subscript notation:
```python
pd = defaultpdict()
pd.foo = 1
assert (pd['foo'] == pd.foo == 1)
```

Set the desired default constructor as normal to avoid having to construct
individual values:
```python
pd = defaultpdict(int)
assert (pd.foo == 0)
```

`list` subscripts also work and return a [`plist`](./pstar_plist.md) of the corresponding keys:
```python
pd = defaultpdict(foo=1, bar=2)
assert (pd[['foo', 'bar']].aslist() == [1, 2])
```

Setting with a `list` subscript also works, using a single element or a matching
`list` for the values:
```python
pd = defaultpdict()
pd[['foo', 'bar']] = 1
assert (pd[['foo', 'bar']].aslist() == [1, 1])
pd[['foo', 'bar']] = [1, 2]
assert (pd[['foo', 'bar']].aslist() == [1, 2])
```

[`update`](./pstar_defaultpdict_update.md) returns `self`, rather than `None`, to support chaining:
```python
pd = defaultpdict(foo=1, bar=2)
pd.update(bar=3).baz = 4
assert (pd.bar == 3)
assert ('baz' in pd.keys())
```

Nested `defaultpdict`s make nice lightweight objects:
```python
pd = defaultpdict(lambda: defaultpdict(list))
pd.foo = 1
pd.stats.bar.append(2)
assert (pd['foo'] == 1)
assert (pd.stats.bar == [2])
```

**Conversion:**

You can convert from `defaultpdict` to `defaultdict` and back using arithmetic operations on
the `defaultpdict` `class` itself, for convenience:
```python
d1 = defaultdict(int, {'foo': 1, 'bar': 2})
pd = defaultpdict * d1
assert (type(d1) == defaultdict)
assert (type(pd) == defaultpdict)
assert (pd == d1)

d2 = pd / defaultpdict
assert (type(d2) == defaultdict)
assert (d2 == d1)
```

See [`pstar`](./pstar_pstar.md) for more details on conversion.

## Methods and Properties:

### [`pstar.defaultpdict.__init__(self, *a, **kw)`](./pstar_defaultpdict___init__.md)

Initialize [`defaultpdict`](./pstar_defaultpdict.md).

### [`pstar.defaultpdict.__getattr__(self, name)`](./pstar_defaultpdict___getattr__.md)

Override `getattr`. If `name` starts with '_', attempts to find that attribute on `self`. Otherwise, looks for a field of that name in `self`.

### [`pstar.defaultpdict.__getitem__(self, key)`](./pstar_defaultpdict___getitem__.md)

Subscript operation. Keys can be any normal `dict` keys or `list`s of such keys.

### [`pstar.defaultpdict.__setattr__(self, name, value)`](./pstar_defaultpdict___setattr__.md)

Attribute assignment operation. Forwards to subscript assignment.

### [`pstar.defaultpdict.__setitem__(self, key, value)`](./pstar_defaultpdict___setitem__.md)

Subscript assignment operation. Keys and values can be scalars or `list`s.

### [`pstar.defaultpdict.__str__(self)`](./pstar_defaultpdict___str__.md)

Readable string representation of `self`.

### [`pstar.defaultpdict.copy(self)`](./pstar_defaultpdict_copy.md)

Copy `self` to new [`defaultpdict`](./pstar_defaultpdict.md). Performs a shallow copy.

### [`pstar.defaultpdict.palues(self)`](./pstar_defaultpdict_palues.md)

Equivalent to `self.values()`, but returns a [`plist`](./pstar_plist.md) with values sorted as in `self.peys()`.

### [`pstar.defaultpdict.peys(self)`](./pstar_defaultpdict_peys.md)

Get `self.keys()` as a sorted [`plist`](./pstar_plist.md).

### [`pstar.defaultpdict.pitems(self)`](./pstar_defaultpdict_pitems.md)

Equivalent to `self.items()`, but returns a [`plist`](./pstar_plist.md) with items sorted as in `self.peys()`.

### [`pstar.defaultpdict.qj(self, *a, **kw)`](./pstar_defaultpdict_qj.md)

Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

### [`pstar.defaultpdict.rekey(self, map_or_fn=None, inplace=False, **kw)`](./pstar_defaultpdict_rekey.md)

Change the keys of `self` or a copy while keeping the same values.

### [`pstar.defaultpdict.update(self, *a, **kw)`](./pstar_defaultpdict_update.md)

Update `self`. **Returns `self` to allow chaining.**

## [Source](../pstar/pstar.py#L491-L914)