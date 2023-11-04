# [`pstar`](./pstar.md).[`ptuple`](./pstar_ptuple.md).`qj(self, *a, **kw)`

Call the `qj` logging function with `self` as the value to be logged. All other arguments are passed through to `qj`.

`qj` is a debug logging function. Calling `ptuple.qj()` is often the fastest way
to begin debugging an issue.

See [qj](https://github.com/iansf/qj) for detailed information on using `qj`.

**Examples:**
```python
pt = ptuple([1, 2.0, 'three'])
pt.qj('pt')
# Logs:
# qj: <calling_module> calling_function: pt <2910>: (1, 2.0, 'three')
```

**Returns:**

>    `self`, as processed by the arguments supplied to `qj`.



## [Source](../pstar/pstar.py#L1083-L1104)