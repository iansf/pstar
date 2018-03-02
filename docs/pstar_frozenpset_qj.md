# [`pstar`](./pstar.md).[`frozenpset`](./pstar_frozenpset.md).`qj(self, *a, **kw)`

Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

`qj` is a debug logging function. Calling `frozenpset.qj()` is often the fastest way
to begin debugging an issue.

See [qj](https://github.com/iansf/qj) for detailed information on using `qj`.

**Examples:**
```python
ps = frozenpset([1, 2.0, 'three'])
ps.qj('ps')
# Logs:
# qj: <calling_module> calling_function: ps <2910>: frozenpset({1, 2.0, 'three'})
```

**Returns:**

>    `self`, as processed by the arguments supplied to `qj`.



## [Source](../pstar/pstar.py#L953-L974)