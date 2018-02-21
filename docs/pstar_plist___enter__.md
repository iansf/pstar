# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`__enter__(self)`

Allow the use of plists in `with` statements.

**Examples:**
```python
import glob, os
path = os.path.dirname(__file__)
filenames = plist(glob.glob(os.path.join(path, '*.py')))
with filenames.apply(open, 'r') as f:
  texts = f.read()
assert (len(texts) >= 1)
assert (len(texts.all(isinstance, str)) >= 1)
```

**Returns:**

>    [`plist`](/docs/pstar_plist.md) of results of calling `__enter__` on each element of `self`.



