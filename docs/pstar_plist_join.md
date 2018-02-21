# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`join(self)`

Adds and returns an outer [`plist`](./pstar_plist.md) around `self`.

**Examples:**

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

**Returns:**

>    plist with one additional level of nesting.



## [Source](../pstar/pstar.py#L3897-L3942)