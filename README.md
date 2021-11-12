# `DHRutil`
Dylan H. Ross

A Python package with utilities for stuff I do a lot.


## `DHRutil.caching`

Provides a decorator that handles caching of return values from functions that take a long time to initialize or 
compute (e.g. results from a long computation), the results of which are not expected to change between 
subsequent calls.

### `DHRutil.caching.cached_rv`

A function decorator that caches the return value from a function the first time it is run, then subsequent calls to
that function (with the same arguments) return the cached results rather than running the actual function. Cached 
return values get saved as `.pickle` files in the `__rvcache__` directory, which must exist before using this decorator
or an exception will be raised.

#### Parameters   
`func` : `function`  
a long-running function that will have return value cached

#### Returns 
`wrapper` : `function`  
wrapped function, either runs the input function or loads cached result

#### Example
```python
from DHRutil.caching import cached_rv

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

## `DHRutil.plotting`
Provides various utilities for making plots using `matplotlib`.

### `DHRutil.plotting.get_colors`

Returns a list of N colors from a specified color set. If N colors exceeds the number in the specified color set, 
then the user is warned and the colors are cycled until the desired N is reached. Available color sets include:
* 'seq7' - a sequential color set with 7 levels for when order is meaningful
* 'nonseq7' - a nonsequential color set with 7 levels for when order is not important (default)

#### Parameters
`n_colors` : `int`  
number of colors to return  
`color_set` : `str`, _default='nonseq7'_  
specify which color set to sample the colors from  

#### Returns 
`colors` : `list(str)`  
list of colors  

#### Example
```python
from DHRutil.plotting import get_colors

# get three colors (unpack from list) from the non-sequential color set
c_A, c_B, c_C = get_colors(3)

# get 5 colors (as list) from the sequential color set
colors = get_colors(5, color_set='seq7')
```

