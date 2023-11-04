# [`pstar`](./pstar.md).`pset(set)`

Placeholder `set` subclass. Mostly unimplemented.

You can construct `pset`s in the normal manners for `set`s:
```python
ps = pset([1, 2.0, 'three'])
ps = pset({1, 2.0, 'three'})
```

`pset` also supports a convenience constructor from a `list` literal:
```python
ps = pset[1, 2.0, 'three']
```

**Conversion:**

You can convert from `pset` to `set` and back using arithmetic
operations on the `pset` `class` itself, for convenience:
```python
s1 = set([1, 2.0, 'three'])
ps = pset * s1
assert (type(s1) == set)
assert (type(ps) == pset)
assert (ps == s1)

s2 = ps / pset
assert (type(s2) == set)
assert (s2 == s1)
```

See [`pstar`](./pstar_pstar.md) for more details on conversion.

## Methods and Properties:

### [`pstar.pset.qj(self, *a, **kw)`](./pstar_pset_qj.md)

Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

## [Source](../pstar/pstar.py#L988-L1042)