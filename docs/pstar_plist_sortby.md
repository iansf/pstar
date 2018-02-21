# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`sortby(self, key=None, reverse=False)`

Sorts `self` and `self.root()` in-place and returns `self`.

`sortby` and [`groupby`](./pstar_plist_groupby.md) work together nicely to create sorted, nested plists.
Note that `sortby` modifies and returns `self`, whereas [`groupby`](./pstar_plist_groupby.md) returns a
new [`plist`](./pstar_plist.md) with a new root. This is because `sortby` doesn't change the
structure of the plist, only the order of its (or its children's) elements.

**Examples:**

A basic sort:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
bar_sorted = foos.bar.sortby()
assert (bar_sorted.aslist() ==
        [0, 0, 1])
foos_sorted_by_bar = bar_sorted.root()
assert (foos_sorted_by_bar.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

Sorting with groups works in the same way -- the sort is applied to each
group of `self`:
```python
by_bar = foos.bar.groupby()
assert (by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
by_bar_sorted = by_bar.bar.sortby(reverse=True)
assert (by_bar_sorted.aslist() ==
        [[1], [0, 0]])
by_bar_sorted = by_bar_sorted.root()
assert (by_bar_sorted.aslist() ==
        [[{'foo': 1, 'bar': 1}],
         [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]])
```

**Args:**

>    **`key`**: Key function to pass to `sorted`. Defaults to the identity function.
>         See the python documentation for `sorted` for more information.

>    **`reverse`**: Boolean specifying whether to sort in reverse order or not.

**Returns:**

>    `self`, sorted.



## [Source](../pstar/pstar.py#L3943-L4002)