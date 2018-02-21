# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`pleft(self)`

Returns a [`plist`](/docs/pstar_plist.md) with the structure of `self` filled `plen(-1)` to 0.

Convenience method identical to `-self.pfill(1) + self.plen(-1, s=True)`.

**Examples:**
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pleft().aslist() ==
        [2, 1, 0])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pleft().aslist() ==
        [[[2], [1]], [[0]]])
assert (foo_by_bar_foo.pleft_().aslist() ==
        [[[1], [0]], [[0]]])
assert (foo_by_bar_foo.pleft(pepth=2).aslist() ==
        [[[0], [0]], [[0]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pleft().aslist() ==
        [[[1], [0]], [[]]])
```

This is useful for calling functions that have some global state that should
change each time a new grouping is started, such as generating many plots
from a single grouped plist using `pyplot`, where the function would need to
call `plt.show()` after each group was completed:
```python
def plot(x, remaining):
  plt.plot(x)

  if remaining == 0:
    plt.show()

(foo.bar == 0).baz = 3 + (foo.bar == 0).foo
(foo.bar == 1).baz = 6
foo.bin = (foo.baz + foo.bar) * foo.foo
by_bar_baz_bin = foo.bar.groupby().baz.groupby().bin.groupby()
by_bar_baz_bin.foo.apply(plot, by_bar_baz_bin.pleft(pepth=2), pepth=2)
```

**Returns:**

>    A [`plist`](/docs/pstar_plist.md) of possibly nested [`plist`](/docs/pstar_plist.md)s where each leaf element is an integer,
>    starting with `self.plen(-1)` in the 'top left' element of the structure
>    and counting down to 0.


