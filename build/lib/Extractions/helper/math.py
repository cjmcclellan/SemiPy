"""This will contain math helper functions"""
import math


def round_to_n(x, n):
    if x == 0:
        return 0
    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))

