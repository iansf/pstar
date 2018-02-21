# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`ungroup(self, r=1, s=None)`

Inverts the last grouping operation applied and returns a new plist.

`ungroup` undoes the last [`groupby`](./pstar_plist_groupby.md) operation by default. It removes
groupings in the inverse order that they are applied in -- [`groupby`](./pstar_plist_groupby.md)
always adds new groups at the inner most layer, so `ungroup` removes
groups from the innermost layer. It does not undo any implicit sorting
caused by the [`groupby`](./pstar_plist_groupby.md) operation, however.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.sortby().groupby()
assert (by_bar.ungroup().aslist() ==
        foos.aslist())

by_bar[0].baz = 6
by_bar[1].baz = by_bar[1].foo * 2
by_bar_baz = by_bar.baz.groupby()
assert (by_bar_baz.ungroup().aslist() ==
        by_bar.aslist())
assert (by_bar_baz.ungroup(2).aslist() ==
        foos.aslist())
assert (by_bar_baz.ungroup(-1).aslist() ==
        by_bar.ungroup(-1).aslist())
```

**Args:**

>    **`r`**: Integer value for the number of groups to remove. If `r == 0`, no
>       groups are removed. If it is positive, that many groups must be
>       removed, or `upgroup` raises a `ValueError`. If `r < 0`, all groups in
>       this plist are removed, returning a flat plist.

>    **`s`**: Successor object. Do not pass -- used to track how many ungroupings
>       have happened so that `ungroup` knows when to stop.

**Returns:**

>    New plist with one or more fewer inner groups, if there were any.

**Raises:**

>    **`ValueError`**: If there are fewer groups to ungroup than requested.



## [Source](../pstar/pstar.py#L4003-L4067)