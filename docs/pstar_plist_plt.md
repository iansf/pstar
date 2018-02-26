# [`pstar`](./pstar.md).[`plist`](./pstar_plist.md).`plt(self, **kwargs)`

Convenience method for managing `matplotlib.pyplot` state within a [`plist`](./pstar_plist.md) chain.

`plt()` serves two purposes:
1. It returns a delegation object that allows calling `pyplot` functions without having to call [`apply`](./pstar_plist_apply.md) -- e.g.,
   `plist.plt().plot()` instead of `plist.apply(plt.plot)`.
1. It allows calling of multiple `pyplot` functions in a single call just by passing `**kwargs`. This
   makes it easier to set up plotting contexts and to control when plots are shown, without adding
   lots of one-line `plt` calls before and after the data processing and plotting code.

Neither of these use cases provides anything that can't be done directly with normal calls to `plt`
functions and `plist.apply`. This method is just to make your life easier if you do a lot of
plotting.

When passing `kwargs` to `plt()`, they are executed in alphabetical order. If that is inappropriate,
(e.g., when creating a figure and setting other parameters), you can break up the call into two or
more `plt()` calls to enforce any desired ordering, but you should probably just do that kind of
complicated setup outside of the [`plist`](./pstar_plist.md) context.

**Examples:**
```python
foos = plist([pdict(foo=i, bar=i % 2) for i in range(5)])
(foos.bar == 0).baz = 3 - ((foos.bar == 0).foo % 3)
(foos.bar == 1).baz = 6

foos.foo.plt().scatter(foos.bar).plt(show=None)
# Equivlent to:
foos.foo.apply(plt.scatter, foos.bar)
plt.show()

by_bar = foos.bar.groupby()
by_bar.foo.plt().plot().plt(show=None)
# Equivlent to:
by_bar.foo.apply(plt.plot)
plt.show()

# Create a figure of size 12x8, set the x and y limits, add x and y axis labels,
# draw a scatter plot with custom colors and labels per group, add the legend, and show the figure.
by_bar.foo.plt(
    figure=dict(figsize=(12, 8)), xlim=(-1, 5), ylim=(-1, 7), xlabel='foo', ylabel='baz'
).scatter(
    by_bar.baz, c=plist['r', 'g'], label='bar: ' + by_bar.bar.puniq().ungroup().pstr()
).plt(legend=dict(loc=0), show=None)

# Equivalent to:
plt.figure(figsize=(12, 8))
plt.xlabel('foo')
plt.xlim((-1, 5))
plt.ylabel('baz')
plt.ylim((-1, 7))
by_bar.foo.apply(plt.scatter, by_bar.baz, c=plist['r', 'g'], label='bar: ' + by_bar.bar.puniq().ungroup().pstr())
plt.legend(loc=0)
plt.show()
```

**Args:**

>    **`**kwargs`**: Key/value pairs where the key is a function name on `plt`, and the value is the arguments
>              to call that function with, or `None` for an empty call.

**Returns:**

>    Delegation object that can call `pyplot` functions like `plt.plot`, as well as accessing whatever
>    properties are available to elements of `self`.



## [Source](../pstar/pstar.py#L3616-L3720)