# Description: Define reflected(swapped arguments) operators that accept only two arguments.
#                We forward all calls to numpy.
# Author: Jaswant Sai Panchumarti

import numpy as np

def add(obj, other):
    return np.add(other, obj)

def sub(obj, other):
    return np.subtract(other, obj)

def mul(obj, other):
    return np.multiply(other, obj)

def matmul(obj, other):
    return np.matmul(other, obj)

def truediv(obj, other):
    return np.true_divide(other, obj)

def floordiv(obj, other):
    return np.floor_divide(other, obj)

def mod(obj, other):
    return np.mod(other, obj)

def divmod(obj, other):
    return np.divmod(other, obj)

def pow(obj, other):
    return np.power(other, obj)

def lshift(obj, other):
    return np.left_shift(other, obj)

def rshift(obj, other):
    return np.right_shift(other, obj)

def logical_and(obj, other):
    return np.logical_and(other, obj)

def logical_or(obj, other):
    return np.logical_or(other, obj)

def logical_xor(obj, other):
    return np.logical_xor(other, obj)
