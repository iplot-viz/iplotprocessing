# Description: Define operators that accept only one argument.
#                We forward all calls to numpy.
# Author: Jaswant Sai Panchumarti

import numpy as np


def neg(obj):
    return -1 * obj


def absolute(obj):
    return np.absolute(obj)


def invert(obj):
    return np.invert(obj)
