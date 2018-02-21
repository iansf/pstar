# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`root(self)`

Returns the root of the [`plist`](/docs/pstar_plist.md).

**Examples:**

When a [`plist`](/docs/pstar_plist.md) is created, by default its root is `self`:
```python
pl = plist([1, 2, 3])
assert (pl.root() is pl)
```

Subsequent calls to the [`plist`](/docs/pstar_plist.md) will return new [`plist`](/docs/pstar_plist.md)s, but most of those
calls will retain the original root:
```python
pl2 = pl + 3
assert (pl2.aslist() ==
        [4, 5, 6])
assert (pl2.root() is pl)
assert (pl2.pstr().root() is pl)
```

Some methods create a new root [`plist`](/docs/pstar_plist.md) in order to keep the values and the root
syncronized:
```python
assert (pl2[0:2].aslist() ==
        [4, 5])
assert (pl2[0:2].root().aslist() ==
        [1, 2])
assert (pl2.sortby(reverse=True).aslist() ==
        [6, 5, 4])
assert (pl2.sortby(reverse=True).root().aslist() ==
        [3, 2, 1])
```

[`plist`](/docs/pstar_plist.md) filtering also always returns the root, in order to make the filter easily chainable:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
filtered = foo.bar == 0
assert (filtered.aslist() ==
        [dict(foo=0, bar=0), dict(foo=2, bar=0)])
assert (filtered.root() is filtered)
(foo.bar == 0).baz = 6
(foo.bar == 1).baz = foo.foo * 2
assert (foo.aslist() ==
        [dict(foo=0, bar=0, baz=6), dict(foo=1, bar=1, baz=2), dict(foo=2, bar=0, baz=6)])
```

Grouping also always returns the root:
```python
by_bar = foo.bar.groupby()
assert (by_bar.aslist() ==
        [[{'bar': 0, 'baz': 6, 'foo': 0}, {'bar': 0, 'baz': 6, 'foo': 2}],
         [{'bar': 1, 'baz': [0, 2, 4], 'foo': 1}]])
assert (by_bar.aslist() == by_bar.root().aslist())
```

**Returns:**

>    The root [`plist`](/docs/pstar_plist.md) of `self`.



