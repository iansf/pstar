# [`pstar`](./pstar.md).`frozenpset(frozenset)`

Placeholder `frozenset` subclass. Mostly unimplemented.

You can construct `frozenpset`s in the normal manners for `frozenset`s:
```python
ps = frozenpset([1, 2.0, 'three'])
ps = frozenpset({1, 2.0, 'three'})
```

`frozenpset` also supports a convenience constructor from a `list` literal:
```python
ps = frozenpset[1, 2.0, 'three']
```

**Conversion:**

You can convert from `frozenpset` to `frozenset` and back using arithmetic
operations on the `frozenpset` `class` itself, for convenience:
```python
s1 = frozenset([1, 2.0, 'three'])
ps = frozenpset * s1
assert (type(s1) == frozenset)
assert (type(ps) == frozenpset)
assert (ps == s1)

s2 = ps / frozenpset
assert (type(s2) == frozenset)
assert (s2 == s1)
```

See [`pstar`](./pstar.md) for more details on conversion.

## Methods and Properties:

### [`pstar.frozenpset.qj(self, *a, **kw)`](./pstar_frozenpset_qj.md)

Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

## [Source](../pstar/pstar.py#L923-L977)