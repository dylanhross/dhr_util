"""
DHRutil/plotting.py
Dylan H. Ross
2021/11/12

Description:
    Provides various utilities for making plots using `matplotlib`.
"""

from warnings import warn
from itertools import cycle


def get_colors(n_colors, color_set='nonseq7'):
    """
    get_colors

    Returns a list of N colors from a specified color set. If N colors exceeds the number in the specified color set, 
    then the user is warned and the colors are cycled until the desired N is reached. Available color sets include:
        * 'seq7' - a sequential color set with 7 levels for when order is meaningful
        * 'nonseq7' - a nonsequential color set with 7 levels for when order is not important (default)

    Parameters
    ----------
    n_colors : int
        number of colors to return
    color_set : str, default='nonseq7'
        specify which color set to sample the colors from

    Returns
    -------
    colors : list(str)
        list of colors
    """
    color_sets = {
        'nonseq7': ['#780B51', '#23E391', '#4D119D', '#FFB359', '#FF85C3', '#196DC1', '#8FF63B'],
        'seq7': ['#0A2F51', '#0F596B', '#16837A', '#1D9A6C', '#3B544', '#92CB5D', '#DEDB85']
    }
    # ensure specified color set is valid
    if color_set not in color_sets:
        msg = 'get_color_scheme: color set "{}" not defined in color_sets'
        raise ValueError(msg.format(color_set))
    # select color set
    cs = color_sets[color_set]
    # warn if color set has fewer levels than number of colors requested
    if n_colors > len(cs):
        msg = 'get_color_scheme: n_colors ({}) > levels in color set "{}" ({}), some colors will be repeated'
        warn(msg.format(n_colors, color_set, len(cs)))
    # return the list of colors
    return [c for n, c in zip([_ for _ in range(n_colors)], cycle(cs))]




