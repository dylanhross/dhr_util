"""
    DHRutil/caching.py
    Dylan H. Ross
    2021/09/17

    Description:
        Provides a decorator that handles caching of return values from functions that take a long time to initialize or 
        compute (e.g. results from a long computation), the results of which are not expected to change between 
        subsequent calls.

        Example:
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
"""

import os
from pickle import load as pload, dump as pdump


def _get_pf_name(fname, *args, **kwargs):
    """
_get_pf_name

uses wrapped function name and args/kwargs to construct a .pickle filename
"""
    name = fname 
    for arg in args:
        name += '_' + str(arg)
    for k in kwargs:
        name += '_' + str(k) + '-' + str(kwargs[k])
    name += '.pickle'
    # ensure the filename contains only characters that are valid in filenames
    name = "".join(_ for _ in name if (_.isalnum() or _ in "._- "))
    return name 


def cached_rv(func):
    """
cached_rv

A function decorator that caches the return value from a function the first time it is run, then subsequent calls to
that function (with the same arguments) return the cached results rather than running the actual function. 

Parameters
----------
func : function
    a long-running function that will have return value cached

Returns
-------
wrapper : function
    wrapped function, either runs the input function or loads cached result
"""
    def wrapper(*args, **kwargs):
        rvdir = os.path.join(os.getcwd(), '__rvcache__')
        pf_path = os.path.join(rvdir, _get_pf_name(func.__name__, *args, **kwargs))
        # check if return value has been cached
        if os.path.isfile(pf_path):
            print('(DHRutil.caching.cached_rv) {} exists, loading from cache'.format(pf_path))
            # skip running the function, return a function that just loads the cached file
            with open(pf_path, 'rb') as pf:
                return pload(pf)
        else:
            print('(DHRutil.caching.cached_rv) {} not found, creating cache'.format(pf_path))
            # compute the return value
            rv = func(*args, **kwargs)
            # cache the variable in a .pickle file 
            if not os.path.isdir(rvdir):
                os.mkdir(rvdir)
            with open(pf_path, 'wb') as pf:
                pdump(rv, pf)
            # return the variable
            return rv
    return wrapper

