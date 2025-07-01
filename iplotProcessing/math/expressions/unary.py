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
