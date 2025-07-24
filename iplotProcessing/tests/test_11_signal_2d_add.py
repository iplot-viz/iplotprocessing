# Description: Tests addition of two or more 2D signals.
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.common.grid_mixing import GridAlignmentMode
from iplotProcessing.common.interpolation import InterpolationKind
from iplotProcessing.math.pre_processing.grid_mixing import align
import numpy as np
from iplotProcessing.core import BufferObject, Signal


class TestSignal2DAdd(unittest.TestCase):
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
        align([self.s1, self.s2, self.s3], self.s1, mode=GridAlignmentMode.UNION, kind=InterpolationKind.LINEAR)
        res = self.s1 + self.s2 + self.s3
        expected = (
            b'\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x03\x00\x00\x00\x00\x00\x00\x00'
            b'\x06\x00\x00\x00\x00\x00\x00\x00'
            b'\x09\x00\x00\x00\x00\x00\x00\x00'
        )
        self.assertEqual(res.data.tobytes(), expected)

    def test_signal_ufunc_advanced_1(self):
        # no changes here
        pass

    def test_bo_ufunc_advanced_2(self):
        # no changes here
        pass
