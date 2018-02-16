# pstar
## better python collections


## Overview:


## Examples:


## Philosophy:


## Basic Usage:

### Install with pip:
```
$ pip install pstar
```

### Add the following import:
```
from pstar import *
```


## Advanced Usage:

### `pstar`

`pstar` module.

Import like this:
```python
from pstar import defaultpdict, pdict, plist, pset
```
#### `pstar.defaultpdict`

defaultdict subclass where everything is automatically a property.

Use with dot notation or subscript notation:
```python
  p = defaultpdict()
  p.foo = 1
  assert (p['foo'] == 1)
```

List subscripts also work and return a plist of the corresponding keys:
```python
  p = defaultpdict(foo=1, bar=2)
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

Setting with a list subscript also works, using a single element or a matching
list for the values:
```python
  p = defaultpdict()
  p[['foo', 'bar']] = 1
  assert (p[['foo', 'bar']].aslist() == [1, 1])
  p[['foo', 'bar']] = [1, 2]
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

defaultpdict.update() returns self, rather than None, to support chaining:
```python
  p = defaultpdict(foo=1, bar=2)
  p.update(bar=3).baz = 4
  assert (p.bar == 3)
  assert ('baz' in p.keys())
```

Set the desired defualt constructor as normal to avoid having to construct
individual values:
```python
  p = defaultpdict(int)
  assert (p.foo == 0)
```

Nested defaultpdicts make nice lightweight objects:
```python
  p = defaultpdict(lambda: defaultpdict(list))
  p.foo = 1
  p.stats.bar.append(2)
  assert (p['foo'] == 1)
  assert (p.stats.bar == [2])
```
##### `pstar.defaultpdict.__getattr__`

Override getattr. If `name` starts with '_', attempts to find that attribute on `self`. Otherwise, looks for a field of that name in `self`.

##### `pstar.defaultpdict.__getitem__`

Subscript operation. Keys can be scalars or lists.

##### `pstar.defaultpdict.__init__`

Initialize defaultpdict.

##### `pstar.defaultpdict.__setattr__`

Attribute assignment operation. Forwards to subscript assignment.

##### `pstar.defaultpdict.__setitem__`

Subscript assignment operation. Keys and values can be scalars or lists.

##### `pstar.defaultpdict.copy`

Copy self to new defaultpdict.

##### `pstar.defaultpdict.palues`

Equivalent to `self.values()`, but results are sorted as in `self.peys()`.

##### `pstar.defaultpdict.peys`

Get self.keys() as a sorted plist.

##### `pstar.defaultpdict.pitems`

Equivalent to `self.items()`, but results are sorted as in `self.peys()`.

##### `pstar.defaultpdict.qj`

Call `qj` logging function with `self` as the item to be logged. All other arguments are passed through to `qj`.

##### `pstar.defaultpdict.rekey`

Change the keys of `self` or a copy while keeping the same values.

##### `pstar.defaultpdict.update`

Update self. Returns self.

#### `pstar.pdict`

dict subclass where everything is automatically a property.

Use with dot notation or subscript notation:
```python
  p = pdict()
  p.foo = 1
  assert (p['foo'] == p.foo == 1)
```

List subscripts also work and return a plist of the corresponding keys:
```python
  p = pdict(foo=1, bar=2)
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

Setting with a list subscript also works, using a single element or a matching
list for the values:
```python
  p = pdict()
  p[['foo', 'bar']] = 1
  assert (p[['foo', 'bar']].aslist() == [1, 1])
  p[['foo', 'bar']] = [1, 2]
  assert (p[['foo', 'bar']].aslist() == [1, 2])
```

pdict.update() returns self, rather than None, to support chaining:
```python
  p = pdict(foo=1, bar=2)
  p.update(bar=3).baz = 4
  assert (p.bar == 3)
  assert ('baz' in p.keys())
```
##### `pstar.pdict.__getitem__`

Subscript operation. Keys can be scalars or lists.

##### `pstar.pdict.__init__`

Initialize pdict.

##### `pstar.pdict.__setitem__`

Subscript assignment operation. Keys and values can be scalars or lists.

##### `pstar.pdict.copy`

Copy self to new pdict.

##### `pstar.pdict.palues`

Equivalent to `self.values()`, but results are sorted as in `self.peys()`.

##### `pstar.pdict.peys`

Get self.keys() as a sorted plist.

##### `pstar.pdict.pitems`

Equivalent to `self.items()`, but results are sorted as in `self.peys()`.

##### `pstar.pdict.qj`

Call `qj` logging function with `self` as the item to be logged. All other arguments are passed through to `qj`.

##### `pstar.pdict.rekey`

Change the keys of `self` or a copy while keeping the same values.

##### `pstar.pdict.update`

Update self. Returns self.

#### `pstar.plist`

List where everything is automatically a property that is applied to its elements. Guaranteed to surprise, if not delight.

See README.md for a detailed overview of ways plist can be used.
See tests/pstar_test.py for usage examples ranging from simple to complex.
##### `pstar.plist._`

Causes the next call to `self` to be performed as deep as possible in the plist.

##### `pstar.plist.binary_op`

plist-compatible binary operation; applied element-wise to its args.

Args:
  self: plist object.
  other: Object to perform the binary operation with.

Returns:
  A new plist, where each element of `self` had the operation passed to
  `_build_binary_op` applied to it and `other`, or the corresponding element
  of `other`, if the lengths of `self` and `other` match.


##### `pstar.plist.logical_op`

plist-compatible logical operation; performs a set operation on its args.

Args:
  self: plist object.
  other: Object to perform the logical operation with.

Returns:
  A new plist, merging `self` and other according to the operation provided
  to `_build_logical_op`.


##### `pstar.plist.__call__`

Call each element of self, possibly recusively.

Args:
  *args: The arguments to apply to the callables in self.
  **kwargs: The keyword arguments to apply to the callables in self.
            pepth and call_pepth are updated before calling the callables.

Returns:
  A new plist with the return values of calling each callable in self.


##### `pstar.plist.comparator`

plist-compatible comparison operator. Note: comparisons filter plists.

plist comparators can filter on leaf values:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
zero_bars = foo.bar == 0
assert (zero_bars.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
nonzero_bars = foo.bar != 0
assert (nonzero_bars.aslist() ==
        [{'foo': 1, 'bar': 1}])
```

They can also filter on other plists so long as the structures are
compatible:
```python
assert ((foo == zero_bars).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
assert ((foo.foo > foo.bar).aslist() ==
        [{'foo': 2, 'bar': 0}])
```

The same is true when comparing against lists with compatible structure:
```python
assert ((foo.foo == [0, 1, 3]).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

This all generalizes naturally to plists that have been grouped:
```python
foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
nonzero_foo_by_bar_foo = foo_by_bar_foo.bar > 0
assert (nonzero_foo_by_bar_foo.aslist() ==
        [[[],
          []],
         [[{'bar': 1, 'foo': 1}]]])
zero_foo_by_bar_foo = foo_by_bar_foo.foo != nonzero_foo_by_bar_foo.foo
assert (zero_foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[]]])
assert ((foo_by_bar_foo.foo == [[[0], [3]], [[1]]]).aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          []],
         [[{'foo': 1, 'bar': 1}]]])
```

Lists with incompatible structure are compared to `self` one-at-a-time,
resulting in set-like filtering where the two sets are merged with an 'or':
```python

assert ((foo.foo == [0, 1, 3, 4]).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])

assert ((foo_by_bar_foo.foo == [0, 1, 3, 4]).aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          []],
         [[{'foo': 1, 'bar': 1}]]])
```

When comparing against an empty list, `==` always returns an empty list, but
all other comparisons return `self`:
```python
assert ((foo.foo == []).aslist() == [])
assert ((foo.foo < []).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert ((foo_by_bar_foo == nonzero_foo_by_bar_foo).aslist() ==
        [[[],
          []],
         [[{'foo': 1, 'bar': 1}]]])
assert ((foo_by_bar_foo.foo > nonzero_foo_by_bar_foo.foo).aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[]]])
```

Args:
  self: plist object.
  other: Object to compare against.
  return_inds: Optional bool. When `True`, causes the comparison to return
               the plist indices of the matching items. When `False`
               (the default), causes the comparison to return a plist of the
               matching values.

Returns:
  A new plist, filtered from `self` and `other` according to the operation
  provided to `_build_comparator`, if `return_inds` is `False`. Otherwise,
  returns the corresponding indices into self.


##### `pstar.plist.__contains__`

Implements the `in` operator to avoid inappropriate use of plist comparators.

##### `pstar.plist.__delattr__`

Recursively attempt to get the attribute `name`.

Args:
  name: Name of attribute to delete.

Returns:
  self, in order to allow chaining through `pl.__delattr__(name).foo`.


##### `pstar.plist.__delitem__`

Deletes items of self using a variety of potential indexing styles.

Args:
  key: The key to index by.
       The key can be applied to self directly as:
         A list of ints: Deletes from self using those ints as indices.
         A slice: Deletes from self based on the slice.
         An int: Deletes the value at that index.
       The key can be applied to elements of self individually:
         A generic list: Deletes from the elements of self using the
                         elements of the key in order on the elements of
                         self.
         A tuple when the elements of self can be indexed by tuple:
                  Deletes from the elements of self by applying that tuple
                  to each element of self.
         A tuple, otherwise:
                  Deletes from the elements of self where each element gets
                  each element in the key tuple deleted. E.g.,
                  `del foo[('bar', 'baz')]` deletes all `'bar'` and `'baz'`
                  keys from each element of foo.
         Anything else: Deletes the key from each of its elements.

Returns:
  self, in order to allow chaining through `pl.__delitem__(key).foo`.

Raises:
  TypeError: If the key fails to be applied directly to self and fails to be
             applied to its elements individually.


##### `pstar.plist.__delslice__`

Delegates to __delitem__ for compatibility with python 2.7.

##### `pstar.plist.__enter__`

Allow the use of plists in `with` statements.

##### `pstar.plist.__exit__`

Allow the use of plists in `with` statements.

##### `pstar.plist.__getattr__`

Recursively attempt to get the attribute `name`.

Args:
  name: Attribute name.
  _pepth: plist depth at which the found attribute should be applied.
          If _pepth < 0, the attribute is applied as deep as possible, which
          may be on the deepest non-plist children. This permits calling,
          for example, list methods on lists nested inside of plists.
          If _pepth > 0, the attribute is applied after that many recursive
          calls, and any exception generated is propogated back.

Returns:
  Either the value of the attribute, for known non-callable attributes like
  `__class__`, or a callable wrapping the final attributes.


##### `pstar.plist.__getattribute__`

Returns a plist of the attribute for self, or for each element.

Args:
  name: Name of the attribute.

Returns:
  If `name` exists as an attribute of plist, that attribute is returned.
  Otherwise, removes trailing underscores from `name` (apart from those
  normally part of a `__*__` name), and uses the count of underscores to
  indicate how deep into the plist `name` should be searched for. Attempts
  to find the modified `name` on plist first, and then looks for `name` on
  each element of self.

  When attempting to find `name` on the elements of self, first it checks
  if the elements all have `name` as an attribute. If so, it returns that
  attribute (`[getattr(x, name) for x in self]`). Otherwise, it attempts to
  return `name` as an index of each element (`[x[name] for x in self]`).

Raises:
  AttributeError: If `name` is not found on self or the elements of self.


##### `pstar.plist.__getitem__`

Returns a new plist using a variety of potential indexing styles.

Args:
  key: The key to index by.
       The key can be applied to self directly as:
         A list of ints: Returns a plist using those ints as indices.
         A slice: Returns a plist based on the slice.
         An int: Returns the value at that index (may not be a plist).
       The key can be applied to elements of self individually:
         A generic list: Returns a plist using the elements of the key in
                         order on the elements of self.
         A tuple when the elements of self can be indexed by tuple:
                  Returns a plist applying that tuple to each element of
                  self.
         A tuple, otherwise:
                  Returns a plist where each element of the new plist is a
                  tuple of each value in the key tuple applied to each
                  element of self. E.g., `foo[('bar', 'baz')]` might return
                  `plist([(1, 2), (3, 4), ...])`.
         Anything else: Returns a plist of the key applied to each of its
                        elements.

Returns:
  A plist based on the order of attempting to apply the key described above.

Raises:
  TypeError: If the key fails to be applied directly to self and fails to be
             applied to its elements individually.


##### `pstar.plist.__getslice__`

Delegates to __getitem__ for compatibility with python 2.7.

##### `pstar.plist.__init__`

Constructs plist.

Args:
  *args: Passed directly to list constructor.
  **kwargs: Should only contain 'depth' and 'root' as optional keywords. All
            other keys are passed directly to list constructor.

Returns:
  None. plist is initialized.


##### `pstar.plist.unary_op`

plist-compatible unary operation; applied element-wise to its args.

Args:
  self: plist object.

Returns:
  A new plist, where each element of `self` had the operation passed to
  `_build_unary_op` applied to it.


##### `pstar.plist.__setattr__`

Sets an attribute on a plist or its elements to `val`.

Args:
  name: Name of the attribute to set.
  val: Value to set the attribute to. If val is a sequence and its length
       matches len(self), the elements of val are set on the elements of
       self. Otherwise, the elements of self are all set to val.

Returns:
  self, in order to allow chaining through `pl.__setattr__(name, val).foo`.


##### `pstar.plist.__setitem__`

Sets items of self using a variety of potential indexing styles.

Args:
  key: The key to index by.
       The key can be applied to self directly as:
         A list of ints: Sets items using those ints as indices.
         A slice: Sets items based on the slice.
         An int: Sets the item at that index.
       The key can be applied to elements of self individually:
         A generic list: Sets the items of self using the elements of the
                         key in order.
         A tuple when the elements of self can be indexed by tuple:
                  Sets the elements of self using that tuple to index into
                  each element.
         A tuple, otherwise:
                  Sets the elements of self using each element of the tuple
                  key tuple on each element. E.g., `foo[('bar', 'baz')] = 1`
                  will set the `bar` and `baz` keys of `foo` to `1`.
         Anything else: Sets the elements of self indexed by key to `val`.
  val: Value to assign. If val is a sequence and its length matches either
       `len(self)` (in most cases described above for `key`) or `len(key)`,
       each element of val is applied to each corresponding element of
       `self` or `self[k]`.

Returns:
  self, in order to allow chaining through `pl.__setitem__(key, val).foo`.

Raises:
  TypeError: If the key fails to be applied directly to self and fails to be
             applied to its elements individually.


##### `pstar.plist.__setslice__`

Delegates to __setitem__ for compatibility with python 2.7.

##### `pstar.plist.all`

Returns self if args[0] evaluates to True for all elements of self.

Shortcuts if args[0] ever evaluates to False.
If args are not passed, the function evaluated is `bool`.

Args:
  *args: Optional. If present, the first entry must be a function to evaluate.
         All other args are passed through to that function. If absent, the
         function is set to bool.
  **kwargs: Passed through to the function specified in *args.

Returns:
  `self` or an empty plist (which evaluates to False).


##### `pstar.plist.any`

Returns self if args[0] evaluates to True for any element of self.

Shortcuts as soon as args[0] evaluates to True.
If args are not passed, the function evaluated is `bool`.

Args:
  *args: Optional. If present, the first entry must be a function to evaluate.
         All other args are passed through to that function. If absent, the
         function is set to bool.
  **kwargs: Passed through to func.

Returns:
  `self` or an empty plist (which evaluates to False).


##### `pstar.plist.apply`

Apply an arbitrary function to elements of self, forwarding arguments.

Args:
  func: callable or string name of method in plist class.
  *args: Arguments to pass to func.
  **kwargs: Keyword arguments to pass to `func`, after extracting:
            `paslist`: Boolean (default `False`). If `True`, converts
                       elements of self to list using `plist.aslist()`
                       before passing them to `func`, and reconverts the
                       result of each call to a plist. Note that this does
                       not guarantee that the returned plist has the same
                       shape as `self`, as plist.aslist() recursively
                       converts all contained plists to lists, but `func`
                       might return any arbitrary result, so the same
                       conversion cannot be inverted automatically.
            `psplat`: Boolean (default `False`). If `True`, expands the
                      arguments provided by `self` with the `*` operator
                      (sometimes called the 'splat' operator).

Returns:
  plist resulting from applying func to each element of self.


##### `pstar.plist.aslist`

Recursively convert all nested plists from self to lists, inclusive.

##### `pstar.plist.astuple`

Recursively convert all nested plists from self to tuples, inclusive.

##### `pstar.plist.copy`

Copy self to new plist.

##### `pstar.plist.enum`

Wrap the current plist values in tuples where the first item is the index.

##### `pstar.plist.filter`

Filter self by an arbitrary function on elements of self, forwarding arguments.

Args:
  func: callable. Defaults to `bool`. Return value will be cast to `bool`.
  *args: Arguments to pass to func.
  **kwargs: Keyword arguments to pass to `func`, after extracting the same arguments as `plist.apply`:

Returns:
  plist resulting from filtering out elements of `self` for whom `func` evaluated to a False value.


##### `pstar.plist.groupby`

Group self.root() by the values in self.

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

Returns:
  plist with one additional layer of internal plists, where each such plist
  groups together the root elements based on the values in this plist.


##### `pstar.plist.join`

Adds and returns an outer plist around self.

`join` is useful when you wish to call a function on the top-level plist,
but you don't want to stop your call chain:
```python
foo = plist([{'bar': [1, 2, 3]}, {'bar': [4, 5, 6]}])
assert (foo.aslist() ==
        [{'bar': [1, 2, 3]},
         {'bar': [4, 5, 6]}])
arr1 = np.array(foo.bar.pstr().groupby().bar)
assert (np.all(arr1 ==
               np.array([[[1, 2, 3]],
                         [[4, 5, 6]]])))
arr2 = foo.bar.pstr().groupby().bar.np()
assert (np.all(np.array(arr2.aslist()) ==
               np.array([np.array([[1, 2, 3]]),
                         np.array([[4, 5, 6]])])))
arr3 = foo.bar.pstr().groupby().bar.join().np()
assert (np.all(np.array(arr3.aslist()) ==
               np.array([np.array([[[1, 2, 3]],
                                  [[4, 5, 6]]])])))
assert (np.any(arr1 != arr2[0]))
assert (np.all(arr1 == arr3[0]))
```
In the example above, calling `np.array` on the grouped plist gives a
particular array structure, but it does not return a plist, so you can't as
naturally use that array in ongoing computations while keeping track of
the correspondence of the array with the original data in `foo`.

Calling plist.np() directly on the grouped plist gives a different result,
however, as shown in `arr2`. The array is missing one dimension relative to
the call that generated `arr1`.

Instead, it is easy to call `plist.join()` before calling `plist.np()` in
this case in order to get the same result of passing `self` to `np.array()`,
but the advantage is that the numpy array is still wrapped in a plist, so it
can be used in follow-on computations.

Returns:
  plist with one additional level of nesting.


##### `pstar.plist.lfill`

Returns a list with the structure of `self` filled in order from `v`.

Identical to `plist.pfill()`, but returns a list instead of a plist.
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.lfill() ==
        [0, 1, 2])
assert (foo.lfill(-7) ==
        [-7, -6, -5])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.lfill() ==
        [[[0], [1]], [[2]]])
assert (foo_by_bar_foo.lfill_() ==
        [[[0], [1]], [[0]]])
assert (foo_by_bar_foo.lfill(pepth=2) ==
        [[[0], [0]], [[0]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.lfill(3) ==
        [[[3], [4]], [[]]])
```

Args:
  v: Integer. The value to start filling from. Defaults to 0.
  s: Successor object. Do not pass -- used to track the count of calls
     across the recursive traversal of `self`.

Returns:
  A list (not a plist) of possibly nested plists where each leaf element is
  an integer, starting with the value of `v` in the 'top left' element of
  the structure.


##### `pstar.plist.me`

Sets the current plist as a variable available in the caller's context.

`me` is a convenience method to naturally enable long chaining to prepare
the data in the plist for a future call to `apply` or some other call. It
attempts to add the current plist to the caller's context, either as a
local variable, or as a global (module-level) variable. Because it modifies
the caller's frame, it is not recommended for production code, but can be
qutie useful in jupyter notebooks during exploration of datasets.

Using `me` with a local variable requires that the variable already exist in
the local context, and that it be a plist:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foo.baz = 3 * foo.foo + foo.bar
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0, 'baz': 0},
         {'foo': 1, 'bar': 1, 'baz': 4},
         {'foo': 2, 'bar': 0, 'baz': 6}])
def new_context():
  me = plist()
  foo.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.bar)
new_context()
```

The same can work with a name of your choice:
```python
def new_context():
  baz = plist()
  foo.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
new_context()
```

You can pass the plist you want to use instead:
```python
def new_context():
  me2 = plist()
  foo.bar.groupby().baz.sortby_().groupby().me(me2).foo.plt().plot(me2.foo + 1)
new_context()
```

If there isn't a local variable of that name, `me()` will put the plist into
the caller's `globals()` dict under the requested name. The following both
work if there are no local or global variables named `me` or `baz`:
```python
def new_context():
  foo.bar.groupby().baz.sortby_().groupby().me().foo.plt().plot(me.baz)
  foo.bar.groupby().baz.sortby_().groupby().me('baz').foo.plt().plot(baz.baz)
  del globals()['me']
  del globals()['baz']
new_context()
```

Args:
  name_or_plist: String naming a variable in the caller's context or the
                 global (module-level) context, or an existing plist. In
                 both cases, the variable will be overwritten with a plist
                 that is a shallow copy of `self`. Defaults to `'me'`.
  call_pepth: Do not pass. Used by `plist.__call__` to keep track of how
              many stack frames occur between the caller and `me()`.

Returns:
  `self`, permitting continued chaining.

Raises:
  ValueError: If `name_or_plist` is a string, and that name appears in the
              caller's local variables, but does not evaluate to a plist.
  ValueError: If something other than a string or a plist is passed to
              `name_or_plist`.


##### `pstar.plist.none`

Returns self if args[0] evaluates to False for all elements.

Shortcuts if args[0] ever evaluates to evaluates to True.
If args are not passed, the function evaluated is `bool`.

Args:
  *args: Optional. If present, the first entry must be a function to evaluate.
         All other args are passed through to that function. If absent, the
         function is set to bool.
  **kwargs: Passed through to func.

Returns:
  `self` or an empty plist (which evaluates to False).


##### `pstar.plist.nonempty`

Returns a new plist with empty sublists removed.

`nonempty` is useful in combination with grouping and filtering:
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
foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
filtered = foo_by_bar_foo.foo != 1
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
the two ways to call functions on sublists -- passing `pepth` and adding `_`
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

Args:
  r: Integer value for the number of times to recurse. Defaults to 0, which
     causes only empty direct children of `self` to be removed. If `r > 0`,
     `nonempty` recurses `r` times, and then removes empty sublists at that
     depth and empty sublists back up the recursive call chain. If `r < 0`,
     `nonempty` recurses as deep as it can, and then removes empty sublists
     back up the recursive call chain.

Returns:
  New plist with empty sublist removed.


##### `pstar.plist.np`

Converts the elements of self to numpy arrays, forwarding passed args.

##### `pstar.plist.pand`

Stores `self` into a plist of tuples that gets extended with each call.

`pand` is meant to facilitate building up tuples of values to be sent as
a single block to a chained call to `apply`, or as `*args` when calling
`plist.apply(psplat=True)`. The name is `pand` to evoke conjunction: the
caller wants a plist with this *and* this *and* this.

`pand` stores a variable in the caller's frame that isn't visible to the
caller, but is visible to future calls to `pand` due to how `locals()`
works.

Basic usage might look like:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
foo.baz = 3 * foo.foo + foo.bar
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0, 'baz': 0},
         {'foo': 1, 'bar': 1, 'baz': 4},
         {'foo': 2, 'bar': 0, 'baz': 6}])
def new_context():
  assert (foo.bar.groupby().baz.groupby().foo.pand().root().bar.pand().ungroup()
             .apply_(qj, '(foo, bar)') ==
          [[[(0, 0)],
            [(2, 0)]],
           [[(1, 1)]]])
new_context()
# Logs:
#   qj: <pstar> apply: (foo, bar) <1249>: (0, 0)
#   qj: <pstar> apply: (foo, bar) <1249>: (2, 0)
#   qj: <pstar> apply: (foo, bar) <1249>: (1, 1)
```

The same construction can be used with methods that expect the arguments
individually, requiring the tuple to be expanded:
```python
def new_context():
  (foo.bar.groupby().baz.groupby().foo.pand().root().bar.pstr().pand()
      .ungroup().qj('pand').apply_(qj, psplat=True, b=0))
new_context()
```

Building multiple tuples in the same context requires passing `name` to keep
them separate:
```python
def new_context():
  me = plist()
  assert (foo.bar.groupby().baz.groupby().me().foo.pand().root().bar.pand().ungroup()
             .apply_(qj,
                     me.foo.pand('strs').root().bar.pand('strs').ungroup().pstr()) ==
          [[(0, 0),
            (2, 0)],
           [(1, 1)]])
new_context()
# Logs:
#   qj: <pstar> apply: (0, 0) <1249>: (0, 0)
#   qj: <pstar> apply: (2, 0) <1249>: (2, 0)
#   qj: <pstar> apply: (1, 1) <1249>: (1, 1)
```
Note that the construction above is hard to understand, and probably
shouldn't be used.

Args:
  name: String naming an available variable in the caller's context. Should
        only be passed if the calling frame needs to create multiple
        different tuples. Defaults to '__plist_and_var__'. If a variable of
        the same name exists in the caller's context, `pand` will fail to
        write to it.
  call_pepth: Do not pass. Used by `plist.__call__` to keep track of how
              many stack frames occur between the caller and `pand()`.

Returns:
  The current plist of tuples, with `self` added.

Raises:
  ValueError: If the variable named by `name` is already present in the
              caller's frame and is not a plist, or has different `pshape()`
              than `self`.


##### `pstar.plist.pd`

Converts self into a pandas DataFrame, forwarding passed args.

##### `pstar.plist.pdepth`

Returns a plist of the recursive depth of each leaf element, from 0.

`pdepth` returns a plist of the same plist structure as self:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pdepth().aslist() ==
        [0])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pdepth().aslist() ==
        [[[2], [2]], [[2]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pdepth().aslist() ==
        [[[2], [2]], [[]]])
```

Since the depth values are always equal or empty in well-formed plists, it
is sometimes more convenient to get the depth as a scalar value. Pass a True
value to the first parameter (`s` for 'scalar'):
```python
assert (foo.pdepth(s=1) == 0)
assert (foo_by_bar_foo.pdepth(1) == 2)
assert (filtered.pdepth(True) == 2)
```

Args:
  s: Boolean that controls whether a scalar is returned (when `True`) or a
     plist of the same structure as self (when `False`, the default).

Returns:
  plist whose elements are the recursive depth of the leaf children, or a
  scalar representing the maximum depth encountered in self if `s` is
  `True`.


##### `pstar.plist.pequal`

Shortcutting recursive equality function.

`pequal` always returns `True` or `False` rather than a plist. This is a
convenience method for cases when the filtering that happens with `==` is
undesirable or inconvenient.
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
zero_bars = foo.bar == 0
assert (zero_bars.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
assert ((foo == zero_bars).aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0}])
assert (foo.pequal(zero_bars) == False)
```

Args:
  other: Object to check equality against.

Returns:
  True if all elements of self and other are recursively equal.
  False otherwise.


##### `pstar.plist.pfill`

Returns a plist with the structure of `self` filled in order from `v`.

Identical to `plist.lfill()`, but returns a plist instead of a list.
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pfill().aslist() ==
        [0, 1, 2])
assert (foo.pfill(-7).aslist() ==
        [-7, -6, -5])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pfill().aslist() ==
        [[[0], [1]], [[2]]])
assert (foo_by_bar_foo.pfill_().aslist() ==
        [[[0], [1]], [[0]]])
assert (foo_by_bar_foo.pfill(pepth=2).aslist() ==
        [[[0], [0]], [[0]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pfill(3).aslist() ==
        [[[3], [4]], [[]]])
```

Args:
  v: Integer. The value to start filling from. Defaults to 0.
  s: Successor object. Do not pass -- used to track the count of calls
     across the recursive traversal of `self`.

Returns:
  A plist of possibly nested plists where each leaf element is an integer,
  starting with the value of `v` in the 'top left' element of the structure.


##### `pstar.plist.pleft`

Returns a plist with the structure of `self` filled `plen(-1)` to 0.

Convenience method identical to `-self.pfill(1) + self.plen(-1, s=True)`:
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
from a single grouped plist using pyplot, where the function would need to
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

Returns:
  A plist of possibly nested plists where each leaf element is an integer,
  starting with `self.plen(-1)` in the 'top left' element of the structure
  and counting down to 0.


##### `pstar.plist.plen`

Returns a plist of the length of a recursively-selected layer of self.

`plen` returns a plist of the same depth as self, up to `r`:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.plen().aslist() ==
        [3])
assert (foo.plen(1).aslist() ==
        [3])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.plen().aslist() ==
        [2])
assert (foo_by_bar_foo.plen(r=1).aslist() ==
        [[3]])
assert (foo_by_bar_foo.plen(2).aslist() ==
        [[[3]]])
assert (foo_by_bar_foo.plen(-1).aslist() ==
        [[[3]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.plen().aslist() ==
        [2])
assert (filtered.plen(-1).aslist() ==
        [[[2]]])
```

Since the depth values are always equal or empty in well-formed plists, it
is sometimes more convenient to get the depth as a scalar value. Pass a True
value to the first parameter (`s` for 'scalar'):
```python
assert (foo.plen(s=1) == 3)
assert (foo_by_bar_foo.plen(r=2, s=1) == 3)
assert (filtered.plen(-1, s=True) == 2)
```

Args:
  r: Target recursion depth. Defaults to 0. Set to -1 to recurse as deep as
     possible.
  s: Boolean that controls whether a scalar is returned (when `True`) or a
     plist of the same depth as self (when `False`, the default).

Returns:
  plist whose depth equals the requested recursion depth (or less, if
  `r > self.pdepth()`), containing a single value which is the number of
  plist elements at that depth, or that value as a scalar if `s` is `True`.


##### `pstar.plist.puniq`

Returns a new plist with only a single element of each value in self.

`puniq` reduces the values of the groups of self using an equality check:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
reduced = foo.bar.puniq()
assert (reduced.aslist() ==
        [0, 1])
assert (reduced.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

Grouped plists
```python
foo_by_bar = foo.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
reduced = foo_by_bar.bar.puniq()
assert (reduced.aslist() ==
        [[0], [1]])
assert (reduced.root().aslist() ==
        [[{'foo': 0, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
```

The equality check respects the subgroups of self:
```python
foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
reduced_no_effect = foo_by_bar_foo.bar.puniq()
assert (reduced_no_effect.aslist() ==
        [[[0], [0]], [[1]]])
assert (reduced_no_effect.root().aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
```

As with `plist.groupby`, `preduce_eq` relies on the values being hashable.
If, for some reason, you need to reduce by a non-hashable value, you should
convert it to a hashable representation first, for example using
`plist.pstr()` or `plist.apply(id)`:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=0, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 0, 'bar': 0}])
try:
  reduced_crash = foo.puniq()  # CRASHES!
except Exception as e:
  assert (isinstance(e, TypeError))
reduced_pstr = foo.pstr().puniq()
assert (reduced_pstr.aslist() ==
        ["{'bar': 0, 'foo': 0}",
         "{'bar': 1, 'foo': 1}"])
assert (reduced_pstr.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
reduced_id = foo.apply(id).puniq()
assert (reduced_id.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 0, 'bar': 0}])
```
In the last case, since each of the elements of `foo` are unique pdicts,
reducing by `plist.apply(id)` has no useful effect, but if there had been
any duplicates in the elements of `foo`, they would have been removed.

Returns:
  New plist with a new `root` where there is only one example of each value
  in each sublist. The corresponding `root` element is the first element in
  `self.root()` that has that value.


##### `pstar.plist.pset`

Converts the elements of self into pset objects.

##### `pstar.plist.pshape`

Returns a plist of the same structure as self, filled with leaf lengths.

`pshape` returns a plist of the same structure as self:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pshape().aslist() ==
        [3])

foo_by_bar = foo.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'bar': 0, 'foo': 0},
          {'bar': 0, 'foo': 2}],
         [{'bar': 1, 'foo': 1}]])
assert (foo_by_bar.pshape().aslist() ==
        [[2], [1]])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pshape().aslist() ==
        [[[1], [1]], [[1]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pshape().aslist() ==
        [[[1], [1]], [[]]])
```

Returns:
  plist of the same structure as self, where each leaf plist has a single
  element, which is the length of the corresponding leaf plist in `self`.


##### `pstar.plist.pstr`

Returns a plist with leaf elements converted to strings.

##### `pstar.plist.pstructure`

Returns a list of the number of elements in each layer of self.

Gives a snapshot view of the structure of `self`. The length of the returned
list is the depth of `self`. Each value in the list is the result of calling
`self.plen(r)`, where `r` ranges from 0 to `self.pdepth()`. `plen(r)` gives
the sum of the lengths of all plists at layer `r`.
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.pstructure().aslist() ==
        [3])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.pstructure().aslist() ==
        [2, 3, 3])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
assert (filtered.pstructure().aslist() ==
        [2, 3, 2])
```

Returns:
  A list (not a plist) of `self.pdepth()` integers, where each integer is
  the number of elements in all plists at that layer, 0-indexed according to
  depth.


##### `pstar.plist.puniq`

Returns a new plist with only a single element of each value in self.

`puniq` reduces the values of the groups of self using an equality check:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
reduced = foo.bar.puniq()
assert (reduced.aslist() ==
        [0, 1])
assert (reduced.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

Grouped plists
```python
foo_by_bar = foo.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
reduced = foo_by_bar.bar.puniq()
assert (reduced.aslist() ==
        [[0], [1]])
assert (reduced.root().aslist() ==
        [[{'foo': 0, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
```

The equality check respects the subgroups of self:
```python
foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
reduced_no_effect = foo_by_bar_foo.bar.puniq()
assert (reduced_no_effect.aslist() ==
        [[[0], [0]], [[1]]])
assert (reduced_no_effect.root().aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
```

As with `plist.groupby`, `preduce_eq` relies on the values being hashable.
If, for some reason, you need to reduce by a non-hashable value, you should
convert it to a hashable representation first, for example using
`plist.pstr()` or `plist.apply(id)`:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=0, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 0, 'bar': 0}])
try:
  reduced_crash = foo.puniq()  # CRASHES!
except Exception as e:
  assert (isinstance(e, TypeError))
reduced_pstr = foo.pstr().puniq()
assert (reduced_pstr.aslist() ==
        ["{'bar': 0, 'foo': 0}",
         "{'bar': 1, 'foo': 1}"])
assert (reduced_pstr.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1}])
reduced_id = foo.apply(id).puniq()
assert (reduced_id.root().aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 0, 'bar': 0}])
```
In the last case, since each of the elements of `foo` are unique pdicts,
reducing by `plist.apply(id)` has no useful effect, but if there had been
any duplicates in the elements of `foo`, they would have been removed.

Returns:
  New plist with a new `root` where there is only one example of each value
  in each sublist. The corresponding `root` element is the first element in
  `self.root()` that has that value.


##### `pstar.plist.qj`

Applies logging function qj to self for easy in-chain logging.

Args:
  *args: Arguments to pass to qj.
  **kwargs: Keyword arguments to pass to qj.

Returns:
  self


##### `pstar.plist.remix`

Returns a new plist of pdicts based on selected data from self.

`remix` allows you to easily restructure your data into a manageable form:
```python
foo = plist([{'foo': 0, 'bar': {'baz': 13, 'bam': 0, 'bin': 'not'}},
             {'foo': 1, 'bar': {'baz': 42, 'bam': 1, 'bin': 'good'}},
             {'foo': 2, 'bar': {'baz': -9, 'bam': 0, 'bin': 'data'}}])
rmx = foo.remix('foo', baz=foo.bar.baz)
assert (rmx.aslist() ==
        [{'foo': 0, 'baz': 13},
         {'foo': 1, 'baz': 42},
         {'foo': 2, 'baz': -9}])
```
Note that `rmx.baz` gets its values from `foo.bar.baz` in a natural manner.

If `remix` is called on a grouped plist, the result is still a flat plist
of flat pdicts, but the values in the pdicts are themselves pdicts:
```python
foo_by_bam = foo.bar.bam.groupby()
assert (foo_by_bam.aslist() ==
        [[{'foo': 0, 'bar': {'bam': 0, 'baz': 13, 'bin': 'not'}},
          {'foo': 2, 'bar': {'bam': 0, 'baz': -9, 'bin': 'data'}}],
         [{'foo': 1, 'bar': {'bam': 1, 'baz': 42, 'bin': 'good'}}]])
rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz)
assert (rmx_by_bam.aslist() ==
        [{'foo': [0, 2], 'baz': [13, -9]},
         {'foo': [1],    'baz': [42]}])
```

This behavior can be useful when integrating with pandas, for example:
```python
df = rmx_by_bam.pd()
# df is the following dataframe object:
#           baz     foo
#   0  [13, -9]  [0, 2]
#   1      [42]     [1]
```

If you instead want `remix` to return grouped pdicts, just pass `pepth=-1`
to have it execute on the deepest plists, as with any other call to a plist:
```python
rmx_by_bam = foo_by_bam.remix('foo', baz=foo_by_bam.bar.baz, pepth=-1)
assert (rmx_by_bam.aslist() ==
        [[{'foo': 0, 'baz': 13},
          {'foo': 2, 'baz': -9}],
         [{'foo': 1, 'baz': 42}]])
```

Args:
  *args: List of property names of items in `self` to include in the remix.
  **kwargs: Key/value pairs where the key will be a new property on items in
            the remix and the value is a deepcast and set to that key.

Returns:
  Flat plist of flat pdicts based on data from self and the passed arguments
  and keyword arguments.


##### `pstar.plist.root`

Returns the root of the plist.

Most plist methods maintain the root pointer so that it is possible to
return to the plist from which later results are generated.


##### `pstar.plist.sortby`

Sorts self and self.root() in-place and returns self.

`sortby` and `groupby` work together nicely to create sorted, nested plists.
Note that `sortby` modifies and returns self, whereas `groupby` returns a
new plist with a new root. This is because `sortby` doesn't change the
structure of the plist, only the order of its (or its children's) elements.

A basic sort:
```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
bar_sorted = foo.bar.sortby()
assert (bar_sorted.aslist() ==
        [0, 0, 1])
foo_sorted_by_bar = bar_sorted.root()
assert (foo_sorted_by_bar.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 2, 'bar': 0},
         {'foo': 1, 'bar': 1}])
```

Sorting with groups works in the same way -- the sort is applied to each
group of `self`:
```python
foo_by_bar = foo.bar.groupby()
assert (foo_by_bar.aslist() ==
        [[{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}],
         [{'foo': 1, 'bar': 1}]])
bar_by_bar_sorted = foo_by_bar.bar.sortby(reverse=True)
assert (bar_by_bar_sorted.aslist() ==
        [[1], [0, 0]])
foo_by_bar_sorted = bar_by_bar_sorted.root()
assert (foo_by_bar_sorted.aslist() ==
        [[{'foo': 1, 'bar': 1}],
         [{'foo': 0, 'bar': 0},
          {'foo': 2, 'bar': 0}]])
```

Args:
  key: Key function to pass to `sorted`. Defaults to the identity function.
       See the python documentation for `sorted` for more information.
  reverse: Boolean specifying whether to sort in reverse order or not.

Returns:
  self, sorted.


##### `pstar.plist.ungroup`

Inverts the last grouping operation applied and returns a new plist.

Args:
  r: Integer value for the number of groups to remove. If `r == 0`, no
     groups are removed. If it is positive, that many groups must be
     removed, or `upgroup` throws a `ValueError`. If `r < 0`, all groups in
     this plist are removed, returning a flat plist.
  s: Successor object. Do not pass -- used to track how many ungroupings
     have happened so that `ungroup` knows when to stop.

Returns:
  New plist with one or more fewer inner groups, if there were any.

Raises:
  ValueError: If there are fewer groups to ungroup than requested.


##### `pstar.plist.uproot`

Sets the root to `self` so future `root()` calls return this plist.

##### `pstar.plist.values_like`

Returns a plist with the structure of `self` filled with `value`.

```python
foo = plist([pdict(foo=0, bar=0), pdict(foo=1, bar=1), pdict(foo=2, bar=0)])
assert (foo.aslist() ==
        [{'foo': 0, 'bar': 0},
         {'foo': 1, 'bar': 1},
         {'foo': 2, 'bar': 0}])
assert (foo.values_like(1).aslist() ==
        [1, 1, 1])

foo_by_bar_foo = foo.bar.groupby().foo.groupby()
assert (foo_by_bar_foo.aslist() ==
        [[[{'foo': 0, 'bar': 0}],
          [{'foo': 2, 'bar': 0}]],
         [[{'foo': 1, 'bar': 1}]]])
assert (foo_by_bar_foo.values_like('foo').aslist() ==
        [[['foo'], ['foo']], [['foo']]])
all_the_same_dict = foo_by_bar_foo.values_like({}, pepth=2)
assert (all_the_same_dict.aslist() ==
        [[[{}], [{}]], [[{}]]])

all_the_same_dict.ungroup(-1)[0].update(foo=1)
assert (all_the_same_dict.aslist() ==
        [[[{'foo': 1}], [{'foo': 1}]], [[{'foo': 1}]]])

filtered = foo_by_bar_foo.bar == 0
assert (filtered.aslist() ==
        [[[{'bar': 0, 'foo': 0}],
          [{'bar': 0, 'foo': 2}]],
         [[]]])
tuples = filtered.values_like((1, 2, 3))
assert (tuples.aslist() ==
        [[[(1, 2, 3)], [(1, 2, 3)]], [[]]])
```
Note the example above that filling with a mutable object like a dict gives
a plist filled that single object, which might be surprising, but is the
same as other common python idioms, such as:
```python
all_the_same_dict = [{}] * 3
assert (all_the_same_dict ==
        [{}, {}, {}])
all_the_same_dict[0].update(foo=1)
assert (all_the_same_dict ==
        [{'foo': 1}, {'foo': 1}, {'foo': 1}])
```

Args:
  value: Value to fill the returned plist with. Can by any python object.

Returns:
  A plist with the structure of `self` filled with `value`.


##### `pstar.plist.zip`

Zips self with others, recursively.

#### `pstar.pset`

Placeholder set subclass. Not yet implemented.

## Testing:

pstar has extensive tests. You can run them with nosetests:
```
$ nosetests
........................................................................................
----------------------------------------------------------------------
Ran 88 tests in 1.341s

OK
```

Or you can run them directly:
```
$ python pstar/tests/pstar_test.py
........................................................................................
----------------------------------------------------------------------
Ran 88 tests in 1.037s

OK
```


## Disclaimer:

This project is not an official Google project. It is not supported by Google
and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.


## Contributing:

See how to [contribute](./CONTRIBUTING.md).


## License:

[Apache 2.0](./LICENSE).