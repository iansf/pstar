# [`pstar`](./pstar.md).`pstar(object)`

Recursively converts between standard python types and pstar types.

**Examples:**

Converting python types to [`pstar`](./pstar.md) types:
```python
data = [dict(foo=[0, 1, 2], bar=dict(bin=0), baz=defaultdict(int, a=1, b=2, c=3)),
        dict(foo=[1, 2, 3], bar=dict(bin=1), baz=frozenset([3, 4, 5])),
        dict(foo=[2, 3, 4], bar=dict(bin=0), baz=set([7, 8, 9]))]

# Recursively convert all pstar-compatible types:
pl = pstar(data)
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [plist, plist, plist])
assert (pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.baz.apply(type).aslist() == [defaultpdict, frozenpset, pset])

# An alternative way to do the same conversion:
pl = pstar * data
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [plist, plist, plist])
assert (pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.baz.apply(type).aslist() == [defaultpdict, frozenpset, pset])

# Only convert the outermost object:
pl = pstar + data
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [dict, dict, dict])
assert (pl.foo.apply(type).aslist() == [list, list, list])
assert (pl.bar.apply(type).aslist() == [dict, dict, dict])
assert (pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])

# The same outer conversion, as a function call:
pl = pstar(data, depth=1)
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [dict, dict, dict])
assert (pl.foo.apply(type).aslist() == [list, list, list])
assert (pl.bar.apply(type).aslist() == [dict, dict, dict])
assert (pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])

# Convert two layers:
pl = pstar(data, depth=2)
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [list, list, list])
assert (pl.bar.apply(type).aslist() == [dict, dict, dict])
assert (pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])

pl = pstar * data

# Convert from pstar types back to python types:
data2 = pl / pstar
assert (data2 == data)
assert (type(data2) == list)
assert ([type(x) for x in data2] == [dict, dict, dict])
assert ([type(x['foo']) for x in data2] == [list, list, list])
assert ([type(x['bar']) for x in data2] == [dict, dict, dict])
assert ([type(x['baz']) for x in data2] == [defaultdict, frozenset, set])

# Only convert the outermost object:
data2 = pl - pstar
assert (data2 == data)
assert (type(data2) == list)
assert ([type(x) for x in data2] == [pdict, pdict, pdict])
assert ([type(x['foo']) for x in data2] == [plist, plist, plist])
assert ([type(x['bar']) for x in data2] == [pdict, pdict, pdict])
assert ([type(x['baz']) for x in data2] == [defaultpdict, frozenpset, pset])
```

You can also convert from each [`pstar`](./pstar.md) class to its python equivalent and back using
arithmetic operations on the `class` itself, for convenience:
```python
d1 = {'foo': 1, 'bar': 2}
pd = pdict * d1
assert (type(d1) == dict)
assert (type(pd) == pdict)
assert (pd == d1)

d2 = pd / pdict
assert (type(d2) == dict)
assert (d2 == d1)

pl = plist * data
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [dict, dict, dict])
assert (pl.foo.apply(type).aslist() == [plist, plist, plist])
assert (pl.bar.apply(type).aslist() == [dict, dict, dict])
assert (pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])

data2 = data * pdict
assert (type(data2) == list)
assert (plist(data2).apply(type).aslist() == [pdict, pdict, pdict])
assert (plist(data2).foo.apply(type).aslist() == [list, list, list])
assert (plist(data2).bar.apply(type).aslist() == [pdict, pdict, pdict])
assert (plist(data2).baz.apply(type).aslist() == [defaultdict, frozenset, set])

pl = plist + data * pdict
assert (type(pl) == plist)
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [list, list, list])
assert (pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.baz.apply(type).aslist() == [defaultdict, frozenset, set])
```

You can't do arbitrary arithmetic with the conversion methods, though.
One conversion method can't directly operate on another:
```python
try:
  plist * pdict * data
except Exception as e:
  assert (isinstance(e, ValueError))
```

If you want to combine multiple conversions, order of operations matters:
```python
pl = plist + pdict * data
assert (type(pl) == plist)
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [list, list, list])
assert (pl.bar.apply(type).aslist() == [pdict, pdict, pdict])

pl = plist * (pdict * data)
assert (type(pl) == plist)
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [plist, plist, plist])
assert (pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
```

You can combine `pstar.pstar` and the [`pstar`](./pstar.md) classes together to do partial conversion:
```python
pl = pstar * data / pset
assert (isinstance(pl, plist))
assert (pl.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.foo.apply(type).aslist() == [plist, plist, plist])
assert (pl.bar.apply(type).aslist() == [pdict, pdict, pdict])
assert (pl.baz.apply(type).aslist() == [defaultpdict, frozenpset, set])
```

The semantics of the operators are:
 - `+` and `-`: Non-recursive conversions (only the operand itself is converted).
 - `*` and `/`: Recursive conversions (the operand and any children are converted).
 - `+` and `*` on the left or right: Convert python classes to [`pstar`](./pstar.md) classes; e.g., `dict` to [`pdict`](./pstar_pdict.md).
 - `-` and `/` on the right: Convert [`pstar`](./pstar.md) classes to python classes; e.g., [`plist`](./pstar_plist.md) to `list`.
 - `-` and `/` on the left: Convert non-[`pdict`](./pstar_pdict.md) [`pstar`](./pstar.md) types to their python equivalents.

Below are examples focused on [`pdict`](./pstar_pdict.md)s, but the same is true for all of the operators:
```python

# Starting from a nested pstar object, you may want to convert pdicts to dicts.
pd = pdict(foo=plist[1, 2, 3], bar=pset[4, 5, 6], baz=pdict(a=7, b=8, d=9))

# Subtracting by pdict will convert a top-level pdict to dict, but will leave other objects alone.
d = pd - pdict
assert (type(d) == dict)
assert (type(d['foo']) == plist)
assert (type(d['bar']) == pset)
assert (type(d['baz']) == pdict)  # Note that the child is still a pdict!

pl = pd.foo - pdict
assert (type(pl) == plist)  # The type is unchanged, since pd.foo is not a pdict
assert (pl is not pd.foo)  # Conversion still creates a new copy, though!
assert (pl == pd.foo)  # But the contents are identical, of course.

# Dividing by pdict will convert any pdict values to dicts, but leave others unchanged.
d = pd / pdict
assert (type(d) == dict)
assert (type(d['foo']) == plist)
assert (type(d['bar']) == pset)
assert (type(d['baz']) == dict)  # Note that the child is a dict!

# You probably shouldn't left-subtract by pdict, but you can. It converts any other pstar classes
# to their python equivalents, but leaves pdicts alone.
pd2 = pdict - pd
assert (type(pd2) == pdict)

l = pdict - pd.foo
assert (type(l) == list)
assert (type(pd.foo) == plist)
assert (l == pd.foo)

# Left division is also not recommended, but it works. It converts all other pstar classes
# to their python equivalents, but leaves pdicts alone.
pd2 = pdict / pd
assert (type(pd2) == pdict)
assert (type(pd2.foo) == list)
assert (type(pd2.bar) == set)
assert (type(pd2.baz) == pdict)
```

The only exceptions are for the [`pstar`](./pstar.md) left subtraction and left division, which are identical
to right subtraction and right division:
```python
d = pd - pstar
assert (type(d) == dict)
assert (type(d['foo']) == plist)
assert (type(d['bar']) == pset)
assert (type(d['baz']) == pdict)

d = pstar - pd
assert (type(d) == dict)
assert (type(d['foo']) == plist)
assert (type(d['bar']) == pset)
assert (type(d['baz']) == pdict)

d = pd / pstar
assert (type(d) == dict)
assert (type(d['foo']) == list)
assert (type(d['bar']) == set)
assert (type(d['baz']) == dict)

d = pstar / pd
assert (type(d) == dict)
assert (type(d['foo']) == list)
assert (type(d['bar']) == set)
assert (type(d['baz']) == dict)
```

You can also access the core [`pstar`](./pstar.md) classes from the [`pstar`](./pstar.md) conversion object:
```python
foos = pstar.plist([pstar.pdict(foo=0, bar=0), pstar.pdict(foo=1, bar=1), pstar.pdict(foo=2, bar=0)])
```

This is convenient if you only imported as `from pstar import pstar`.



## [Source](../pstar/pstar.py#L5628-L5861)