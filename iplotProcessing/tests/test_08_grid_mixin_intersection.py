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
        align(self.signals_set_1, self.signals_set_1[0], mode=GridAlignmentMode.INTERSECTION, kind=InterpolationKind.LINEAR)
        valid_values = [0, 10, 20, 40, 50]
        self.assertListEqual(
            self.signals_set_1[0].time.tolist(),
            valid_values
        )

    def test_align_2(self):
        align(self.signals_set_2, self.signals_set_2[0], mode=GridAlignmentMode.INTERSECTION, kind=InterpolationKind.LINEAR)
        valid_values = [0, 1, 2, 3]
        self.assertListEqual(
            self.signals_set_2[0].time.tolist(),
            valid_values
        )
