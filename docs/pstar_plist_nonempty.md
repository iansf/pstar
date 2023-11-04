# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`nonempty(self, r=0)`

Returns a new [`plist`](./pstar_plist.md) with empty sublists removed.

**Examples:**

`nonempty` is useful in combination with grouping and filtering:
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foos.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
foo_by_bar = foos.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
filtered = foo_by_bar.foo != 1
assert (filtered.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         []])
filtered_nonempty = filtered.nonempty()
assert (filtered_nonempty.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]])
```

If the plist is deep, multiple levels of empty sublists can be removed at
the same time:
```python
by_bar_foo = foos.bar.groupby().foo.groupby()
assert (by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
filtered = by_bar_foo.foo != 1
assert (filtered.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[]]])
filtered_nonempty_0 = filtered.nonempty()
assert (filtered_nonempty_0.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[]]])
filtered_nonempty_1 = filtered.nonempty(1)
assert (filtered_nonempty_1.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]]])
filtered_nonempty_n1 = filtered.nonempty(-1)
assert (filtered_nonempty_n1.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]]])
```
Note that `filtered_nonempty_0` is identical to `filteed`, since there are
no empty sublists at the top level. In this example, `filtered_nonempty_1`
and `filtered_nonempty_n1` give the same result -- the deepest empty sublist
is removed, and then the next deepest empty sublist is removed.

It is also possible to remove empty sublists only at deeper levels, using
the two ways to call functions on sublists -- passing `pepth` and adding [`_`](./pstar_plist__.md)
to the method name:
```python
filtered_nonempty_p1 = filtered.nonempty(pepth=1)
assert (filtered_nonempty_p1.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         []])
filtered_nonempty_u1 = filtered.nonempty_()
assert (filtered_nonempty_u1.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         []])
```
`filtered_nonempty_p1` and `filtered_nonempty_u1` both remove a single layer
of empty sublists starting from one layer into `filtered`.

**Args:**

>    **`r`**: Integer value for the number of times to recurse. Defaults to 0, which
>       causes only empty direct children of `self` to be removed. If `r > 0`,
>       `nonempty` recurses `r` times, and then removes empty sublists at that
>       depth and empty sublists back up the recursive call chain. If `r < 0`,
>       `nonempty` recurses as deep as it can, and then removes empty sublists
>       back up the recursive call chain.

**Returns:**

>    New plist with empty sublist removed.



## [Source](../pstar/pstar.py#L4684-L4782)