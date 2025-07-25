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


# Description: Tests grid intersection alignment mode.
# Author: Jaswant Sai Panchumarti

import unittest
import numpy as np

from iplotProcessing.core import Signal, BufferObject
from iplotProcessing.math.pre_processing.grid_mixing import align
from iplotProcessing.common.grid_mixing import GridAlignmentMode
from iplotProcessing.common.interpolation import InterpolationKind


class TestGridIntersection(unittest.TestCase):
    def setUp(self) -> None:
        sig1 = Signal()
        sig1.data_store[0] = BufferObject(input_arr=[0, 10, 20, 40, 50], unit='s')
        sig1.data_store[1] = BufferObject(input_arr=np.sin(sig1.time), unit='A')

        sig2 = Signal()
        sig2.data_store[0] = BufferObject(input_arr=[30, 50], unit='s')
        sig2.data_store[1] = BufferObject(input_arr=np.sin(sig2.time), unit='A')

        sig3 = Signal()
        sig3.data_store[0] = BufferObject(input_arr=[0, 45], unit='s')
        sig3.data_store[1] = BufferObject(input_arr=np.sin(sig3.time), unit='A')

        self.signals_set_1 = [sig1, sig2, sig3]

        sig1 = Signal()
        sig1.data_store[0] = BufferObject(input_arr=[0, 1, 2, 3], unit='s')
        sig1.data_store[1] = BufferObject(input_arr=np.sin(sig1.time), unit='A')

        sig2 = Signal()
        sig2.data_store[0] = BufferObject(input_arr=[1, 2], unit='s')
        sig2.data_store[1] = BufferObject(input_arr=np.sin(sig2.time), unit='A')

        sig3 = Signal()
        sig3.data_store[0] = BufferObject(input_arr=[3, 4, 5, 6], unit='s')
        sig3.data_store[1] = BufferObject(input_arr=np.sin(sig3.time), unit='A')

        self.signals_set_2 = [sig1, sig2, sig3]
        return super().setUp()

    def test_align_1(self):
        align(self.signals_set_1, mode=GridAlignmentMode.INTERSECTION, kind=InterpolationKind.LINEAR)
        valid_values = [30, 33, 36, 39, 42, 45]
        for sig in self.signals_set_1:
            for v1, v2 in zip(valid_values, sig.time):
                self.assertEqual(v1, v2)

    def test_align_2(self):
        align(self.signals_set_2, mode=GridAlignmentMode.INTERSECTION, kind=InterpolationKind.LINEAR)
        valid_values = [3, 2, 2, 2, 2]
        for sig in self.signals_set_2:
            for v1, v2 in zip(valid_values, sig.time):
                self.assertEqual(v1, v2)
