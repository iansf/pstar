# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`groupby(self)`

Group `self.root()` by the values in `self` and return `self.root()`.

**Examples:**

Given a plist:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
foo_by_bar = foo.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
```
Note that foo_by_bar now has two nested plists. The first inner plist has
the two pdicts where `foo.bar == 0`. The second inner plist has the
remaining pdict where `foo.bar == 1`.

Calling groupby again:
```python
foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
```
Now foo_by_bar_foo has two nested layers of inner plists. The outer nest
groups the values by `bar`, and the inner nest groups them by `foo`.

groupby always operates with leaf children of the plist, and it always adds
new groups as subgroups of the current innermost group.

Grouping relies on the values being hashable. If, for some reason, you need
to group by a non-hashable value, you should convert it to a hashable
representation first, for example using `plist.pstr()` or `plist.apply(id)`:
```python
foo = plist([{'bar': [1, 2, 3]}, {'bar': [1, 2, 3]}])
try:
  foo_by_bar_crash = foo.bar.groupby()  # CRASHES!
except Exception as e:
  assert (isinstance(e, TypeError))
foo_by_bar_pstr = foo.bar.pstr().groupby()
assert (foo_by_bar_pstr.aslist() ==
        [[{'bar': [1, 2, 3]},
          {'bar': [1, 2, 3]}]])
foo_by_bar_id = foo.bar.apply(id).groupby()
assert (foo_by_bar_id.aslist() ==
        [[{'bar': [1, 2, 3]}],
         [{'bar': [1, 2, 3]}]])
```
Note that in the example above, using `pstr()` probably gives the intended
result of grouping both elements together, whereas `apply(id)` gives the
unsurprising result of putting each element into its own group.

**Returns:**

>    plist with one additional layer of internal plists, where each such plist
>    groups together the root elements based on the values in this plist.



## [Source](../pstar/pstar.py#L3990-L4061)