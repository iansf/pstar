# [`pstar`](/docs/pstar.md).[`plist`](/docs/pstar_plist.md).`__getattr__(self, name, _pepth=0)`

Recursively attempt to get the attribute `name`.

Handles getting attributes from `self`, rather than from elements of `self`,
which is handled in `plist.__getattribute__`. The only exception is for
requests to method names that are present on both [`plist`](/docs/pstar_plist.md) and its leaf
elements, for example if the leaves are all `list`s, and a sufficiently high
`_pepth` value, or `_pepth < 0`, in which case the final calls will be
executed on the leaf elements.

The attribute gets wrapped in a callable that handles any requested recursion,
as specified by having called `self._` immediately previously, or due to
trailing '_' in the name that were detected by [`__getattribute__`](/docs/pstar_plist___getattribute__.md).

**Args:**

>    **`name`**: Attribute name.

>    **`_pepth`**: plist depth at which the found attribute should be applied.
>            If _pepth < 0, the attribute is applied as deep as possible, which
>            may be on the deepest non-plist children. This permits calling,
>            for example, list methods on lists nested inside of plists.
>            If _pepth > 0, the attribute is applied after that many recursive
>            calls, and any exception generated is propogated back.

**Returns:**

>    Either the value of the attribute, for known non-callable attributes like
>    `__class__`, or a callable wrapping the final attributes.



