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


# Description: Tests addition of two or more 1D signals.
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.common.grid_mixing import GridAlignmentMode
from iplotProcessing.common.interpolation import InterpolationKind
from iplotProcessing.math.pre_processing.grid_mixing import align
import numpy as np
from iplotProcessing.core import BufferObject, Signal


class TestSignal1DAdd(unittest.TestCase):
    def setUp(self) -> None:
        self.s1 = Signal()
        self.s1.data_store[0] = BufferObject([0, 1, 2, 3])
        self.s1.data_store[1] = BufferObject([0, 1, 2, 3])
        self.s2 = Signal()
        self.s2.data_store[0] = BufferObject([0, 1, 2, 3])
        self.s2.data_store[1] = BufferObject([0, 1, 2, 3])
        self.s3 = Signal()
        self.s3.data_store[0] = BufferObject([0, 1, 2, 3])
        self.s3.data_store[1] = BufferObject([0, 1, 2, 3])
        return super().setUp()

    def test_signal_ufunc_simple(self):
        align([self.s1, self.s2, self.s3], GridAlignmentMode.UNION, kind=InterpolationKind.LINEAR)
        res = self.s1 + self.s2 + self.s3
        self.assertEqual(res.data.tobytes(
        ), b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
           b'\x08@\x00\x00\x00\x00\x00\x00\x18@\x00\x00\x00\x00\x00\x00"@')

    def test_signal_ufunc_advanced_1(self):
        align([self.s1, self.s2, self.s3], GridAlignmentMode.UNION, kind=InterpolationKind.LINEAR)
        res = np.sin(self.s1)
        self.assertEqual(res.data.tobytes(
        ), b'\x00\x00\x00\x00\x00\x00\x00\x00\xee\x0c\t\x8fT\xed\xea?F\xb4\xd1\xea\xf6\x18\xed?[\xd5\xb6m8\x10\xc2?')

    def test_bo_ufunc_advanced_2(self):
        align([self.s1, self.s2, self.s3], GridAlignmentMode.UNION, kind=InterpolationKind.LINEAR)
        res = np.sin(self.s1 + self.s2 + self.s3)
        self.assertEqual(res.data.tobytes(
        ), b'\x00\x00\x00\x00\x00\x00\x00\x00[\xd5\xb6m8\x10\xc2?\xc0\xa2\xb0\x8a\xf1\xe1\xd1\xbf\x91/\x0c6&`\xda?')
