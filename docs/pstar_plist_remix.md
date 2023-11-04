# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`remix(self, *args, **kwargs)`

Returns a new [`plist`](./pstar_plist.md) of `pdicts` based on selected data from `self`.

**Examples:**

`remix` allows you to easily restructure your data into a manageable form:
```python
foos = plist([{'foo': 0, 'bar': {'baz': 13, 'bam': 0, 'bin': 'not'}},
              {'foo': 1, 'bar': {'baz': 42, 'bam': 1, 'bin': 'good'}},
              {'foo': 2, 'bar': {'baz': -9, 'bam': 0, 'bin': 'data'}}])
rmx = foos.remix('foo', baz=foos.bar.baz)
assert (rmx.aslist() ==
        [{'foo': 0, 'baz': 13},
         {'foo': 1, 'baz': 42},
         {'foo': 2, 'baz': -9}])
```
Note that `rmx.baz` gets its values from `foo.bar.baz` in a natural manner.

If `remix` is called on a grouped [`plist`](./pstar_plist.md), the result is still a flat [`plist`](./pstar_plist.md)
of flat [`pdict`](./pstar_pdict.md)s, but the values in the [`pdict`](./pstar_pdict.md)s are themselves [`plist`](./pstar_plist.md)s:
```python
foo_by_bam = foos.bar.bam.groupby()
assert (foo_by_bam.aslist() ==
        [[{'foo': 0, 'bar': {'bam': 0, 'baz': 13, 'bin': 'not'}},
          {'foo': 2, 'bar': {'bam': 0, 'baz': -9, 'bin': 'data'}}],
         [{'foo': 1, 'bar': {'bam': 1, 'baz': 42, 'bin': 'good'}}]])
rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz)
assert (rmx_by_bam.aslist() ==
        [{'foo': [0, 2], 'baz': [13, -9]},
         {'foo': [1],    'baz': [42]}])
```

This behavior can be useful when integrating with `pandas`, for example:
```python
df = rmx_by_bam.pd()
assert (str(df) ==
        '      foo       baz\n'
        '0  [0, 2]  [13, -9]\n'
        '1     [1]      [42]')
```

If you instead want `remix` to return grouped [`pdict`](./pstar_pdict.md)s, just pass `pepth=-1`
to have it execute on the deepest [`plist`](./pstar_plist.md)s, as with any other call to a [`plist`](./pstar_plist.md):
```python
rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz, pepth=-1)
assert (rmx_by_bam.aslist() ==
        [[{'foo': 0, 'baz': 13},
          {'foo': 2, 'baz': -9}],
         [{'foo': 1, 'baz': 42}]])
```

**Args:**

>    **`*args`**: Property names of items in `self` to include in the remix.

>    **`**kwargs`**: Key/value pairs where the key will be a new property on items in
>              the remix and the value is a deepcast and set to that key.

**Returns:**

>    Flat [`plist`](./pstar_plist.md) of flat `pdicts` based on data from `self` and the passed
>    arguments and keyword arguments.



## [Source](../pstar/pstar.py#L4893-L4967)