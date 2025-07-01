# Copyright (c) 2020-2025 ITER Organization,
#               CS 90046
#               13067 St Paul Lez Durance Cedex
#               France
# Author IO
#
# This file is part of iplotprocessing module.
# iplotprocessing python module is free software: you can redistribute it and/or modify it under
# the terms of the MIT license.
#
# This file is part of ITER CODAC software.
# For the terms and conditions of redistribution or use of this software
# refer to the file LICENSE located in the top level directory
# of the distribution package
#


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


def div_mod(obj, other):
    return np.divmod(other, obj)


def power(obj, other):
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
