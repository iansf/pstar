# [`pstar`](/docs/pstar.md).[`pdict`](/docs/pstar_pdict.md).`qj(self, *a, **kw)`

Call the [`qj`](/docs/pstar_defaultpdict_qj.md) logging function with `self` as the value to be logged. All other arguments are passed through to [`qj`](/docs/pstar_defaultpdict_qj.md).

[`qj`](/docs/pstar_defaultpdict_qj.md) is a debug logging function. Calling `pdict.qj()` is often the fastest way
to begin debugging an issue.

See [qj](https://github.com/iansf/qj) for detailed information on using [`qj`](/docs/pstar_defaultpdict_qj.md).

**Examples:**
```python
pd = pdict(foo=1, bar=2.0, baz='three')
pd.qj('pd').update(baz=3).qj('pd now')
assert (pd.baz == 3)
# Logs:
# qj: <calling_module> calling_function: pd <2910>: {'bar': 2.0, 'baz': 'three', 'foo': 1}
# qj: <calling_module> calling_function:  pd now <2910>: {'bar': 2.0, 'baz': 3, 'foo': 1}
```

**Returns:**

>    `self`, as processed by the arguments supplied to [`qj`](/docs/pstar_defaultpdict_qj.md).



