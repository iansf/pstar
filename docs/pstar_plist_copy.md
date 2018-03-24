# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`copy(self)`

Copy `self` to new [`plist`](./pstar_plist.md). Performs a shallow copy.

`self.root()` is copied as well and used to root the copy if
`self.root() is not self`.
If `self.root() is self`, the root is not maintained.

**Examples:**
```python
pl1 = plist[1, 2, 3]
pl2 = pl1.copy()
assert (pl1 is not pl2)
assert (pl1.root() is pl1 and pl2.root() is pl2)

pl3 = pl2 + 1
pl4 = pl3.copy()
assert (pl4.root().aslist() == pl3.root().aslist())
assert (pl4.root() is not pl3.root())
assert (pl4.root().aslist() == pl2.aslist())
assert (pl4.root() is not pl2)
```

**Returns:**

>    Copy of `self` with `self.root()` handled appropriately.



## [Source](../pstar/pstar.py#L3314-L3342)