# `DHRutil`
Dylan H. Ross

A Python package with utilities for stuff I do a lot.


## `DHRutil.caching`

Provides a decorator that handles caching of return values from functions that take a long time to initialize or 
compute (e.g. results from a long computation), the results of which are not expected to change between 
subsequent calls.

### `DHRutil.caching.cached_rv`

A function decorator that caches the return value from a function the first time it is run, then subsequent calls to
that function (with the same arguments) return the cached results rather than running the actual function.

_Parameters_  
`func` : `function`  
a long-running function that will have return value cached

_Returns_  
`wrapper` : `function`  
wrapped function, either runs the input function or loads cached result

_Example_
```python
# not cached, every time this runs we have to re-run the computation
result = really_long_computation(inputs)

# cached, the computation runs the first time, then the cached result is returned subsequently
result = cached_rv(really_long_computation)(inputs)

# caching can also be used with "pie" syntax when the long running function is defined within the script
@cached_rv
def really_long_computation(inputs):
    # ...
    return output
```

