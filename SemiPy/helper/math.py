"""This will contain math helper functions"""
import math
import numpy as np


def round_to_n(x, n):
    if x == 0:
        return 0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


def find_nearest_arg(array, value, axis=None):
    if axis is None:
        return np.argmin(np.abs(array - value))
    else:
        return np.argmin(np.abs(array - value), axis=axis)
