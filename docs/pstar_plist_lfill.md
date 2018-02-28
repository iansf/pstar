# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`lfill(self, v=0, s=None)`

Returns a **`list`** with the structure of `self` filled in order from `v`.

Identical to `plist.pfill()`, but returns a **`list`** instead of a [`plist`](./pstar_plist.md).

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foos.lfill() ==
        [0, 1, 2])
assert (foos.lfill(-7) ==
        [-7, -6, -5])

by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (by_bar_foo.lfill() ==
        [[[0], [1]], [[2]]])
assert (by_bar_foo.lfill_() ==
        [[[0], [1]], [[0]]])
assert (by_bar_foo.lfill(pepth=2) ==
        [[[0], [0]], [[0]]])

filtered = by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.lfill(3) ==
        [[[3], [4]], [[]]])
```

**Args:**

>    **`v`**: Integer. The value to start filling from. Defaults to 0.

>    **`s`**: Successor object. Do not pass -- used to track the count of calls
>       across the recursive traversal of `self`.

**Returns:**

>    A **`list`** (not a [`plist`](./pstar_plist.md)) of possibly nested `list`s where each leaf element is
>    an integer, starting with the value of `v` in the 'top left' element of
>    the structure.



## [Source](../pstar/pstar.py#L5108-L5161)