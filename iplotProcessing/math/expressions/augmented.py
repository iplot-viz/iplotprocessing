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


# Description: Define operators that accept two arguments and return the modified value.
#                We forward all calls to the binary ops
# Author: Jaswant Sai Panchumarti

def add(obj, other):
    obj = obj.__add__(other)
    return obj


def sub(obj, other):
    obj = obj.__sub__(other)
    return obj


def mul(obj, other):
    obj = obj.__mul__(other)
    return obj


def matmul(obj, other):
    obj = obj.__matmul__(other)
    return obj


def truediv(obj, other):
    obj = obj.__truediv__(other)
    return obj


def floordiv(obj, other):
    obj = obj.__floordiv__(other)
    return obj


def mod(obj, other):
    obj = obj.__mod__(other)
    return obj


def div_mod(obj, other):
    obj = obj.__divmod__(other)
    return obj


def power(obj, other):
    obj = obj.__pow__(other)
    return obj


def lshift(obj, other):
    obj = obj.__lshift__(other)
    return obj


def rshift(obj, other):
    obj = obj.__rshift____(other)
    return obj


def logical_and(obj, other):
    obj = obj.__and__(other)
    return obj


def logical_or(obj, other):
    obj = obj.__or__(other)
    return obj


def logical_xor(obj, other):
    obj = obj.__xor__(other)
    return obj
