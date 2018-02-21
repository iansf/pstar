# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`__delattr__(self, name)`

Deletes an attribute on elements of `self`.

This delegates entirely to the elements of `self`, allowing natural
deletion of attributes.

**Examples:**
```python
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
del foos.foo
assert (foos.aslist() ==
        [{'bar': 0}, {'bar': 1}, {'bar': 0}])

# Deletion works on grouped plists as well:
foos = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
by_bar = foos.bar.groupby()

# Assignment to an existing attribute:
del by_bar.foo
assert (by_bar.aslist() ==
        [[{'bar': 0}, {'bar': 0}], [{'bar': 1}]])
```

**Args:**

>    **`name`**: Name of the attribute to delete.

**Returns:**

>    `self`, in order to allow chaining through `plist.__delattr__(name)`.



