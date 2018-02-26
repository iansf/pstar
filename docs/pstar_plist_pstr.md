# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`pstr(self)`

Returns a plist with leaf elements converted to strings.

Calls `str` on each leaf element of self.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.foo.pstr().aslist() ==
        ['0', '1', '2'])

by_bar = foos.bar.groupby()
assert (by_bar.foo.pstr().aslist() ==
        [['0', '2'], ['1']])
```

Note that string concatenation works naturally with [`plist`](./pstar_plist.md)s, so it is easy to build
up a desired string using `plist.pstr`:
```python
assert (('foo: ' + by_bar.foo.pstr() + ', bar: ' + by_bar.bar.pstr()).aslist() ==
        [['foo: 0, bar: 0', 'foo: 2, bar: 0'], ['foo: 1, bar: 1']])
```

If you want the string representation of a layer of a grouped [`plist`](./pstar_plist.md), instead use
`plist.apply(str)` at the desired depth:
```python
assert (by_bar.foo.apply(str).aslist() ==
        ['[0, 2]', '[1]'])
```

**Returns:**

>    [`plist`](./pstar_plist.md) of strings.



## [Source](../pstar/pstar.py#L3561-L3598)