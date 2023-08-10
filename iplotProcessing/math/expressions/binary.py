# Description: Define operators that accept only two arguments.
#                We forward all calls to numpy.
# Author: Jaswant Sai Panchumarti

import numpy as np


def add(obj, other):
    return np.add(obj, other)


def sub(obj, other):
    return np.subtract(obj, other)


def mul(obj, other):
    return np.multiply(obj, other)


def matmul(obj, other):
    return np.matmul(obj, other)


def truediv(obj, other):
    return np.true_divide(obj, other)


def floordiv(obj, other):
    return np.floor_divide(obj, other)


def mod(obj, other):
    return np.mod(obj, other)


def div_mod(obj, other):
    return np.divmod(obj, other)


def power(obj, other):
    return np.power(obj, other)


def lshift(obj, other):
    return np.left_shift(obj, other)


def rshift(obj, other):
    return np.right_shift(obj, other)


def logical_and(obj, other):
    return np.logical_and(obj, other)


def logical_or(obj, other):
    return np.logical_or(obj, other)


def logical_xor(obj, other):
    return np.logical_xor(obj, other)
