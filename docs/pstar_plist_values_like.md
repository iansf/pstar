# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`values_like(self, value=0)`

Returns a [`plist`](./pstar_plist.md) with the structure of `self` filled with `value`.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foos.values_like(1).aslist() ==
        [1, 1, 1])

by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (by_bar_foo.values_like('foo').aslist() ==
        [[['foo'], ['foo']], [['foo']]])
all_the_same_dict = by_bar_foo.values_like({}, pepth=2)
assert (all_the_same_dict.aslist() ==
        [[[{}], [{}]], [[{}]]])

all_the_same_dict.ungroup(-1)[0].update(foo=1)
assert (all_the_same_dict.aslist() ==
        [[[{'foo': 1}], [{'foo': 1}]], [[{'foo': 1}]]])

filtered = by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
tuples = filtered.values_like((1, 2, 3))
assert (tuples.aslist() ==
        [[[(1, 2, 3)], [(1, 2, 3)]], [[]]])
```

Note in the example above that filling with a mutable object like a `dict` gives
a [`plist`](./pstar_plist.md) filled that single object, which might be surprising, but is the
same as other common python idioms, such as:
```python
all_the_same_dict = [{}] * 3
assert (all_the_same_dict ==
        [{}, {}, {}])
all_the_same_dict[0].update(foo=1)
assert (all_the_same_dict ==
        [{'foo': 1}, {'foo': 1}, {'foo': 1}])
```

**Args:**

>    **`value`**: Value to fill the returned [`plist`](./pstar_plist.md) with. Can by any python object.

**Returns:**

>    A [`plist`](./pstar_plist.md) with the structure of `self` filled with `value`.



## [Source](../pstar/pstar.py#L5313-L5375)