# [`pstar`](./pstar.md).`ptuple(tuple)`

Placeholder `tuple` subclass. Mostly unimplemented.

You can construct `ptuple`s in the normal manner for `tuple`s:
```python
pt = ptuple((1, 2.0, 'three'))
```

`ptuple` also supports a convenience constructor from a `list` literal:
```python
pt = ptuple[1, 2.0, 'three']
```

**Conversion:**

You can convert from `ptuple` to `tuple` and back using arithmetic
operations on the `ptuple` `class` itself, for convenience:
```python
t1 = tuple([1, 2.0, 'three'])
pt = ptuple * t1
assert (type(t1) == tuple)
assert (type(pt) == ptuple)
assert (pt == t1)

t2 = pt / ptuple
assert (type(t2) == tuple)
assert (t2 == t1)
```

See [`pstar`](./pstar_pstar.md) for more details on conversion.

## Methods and Properties:

### [`pstar.ptuple.qj(self, *a, **kw)`](./pstar_ptuple_qj.md)

Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

## [Source](../pstar/pstar.py#L1049-L1102)