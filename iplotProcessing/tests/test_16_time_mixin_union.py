import unittest

from iplotProcessing.core import Signal, BufferObject
from iplotProcessing.math.pre_processing.time_mixing import time_align
from iplotProcessing.common.time_mixing import TimeAlignmentMode
from iplotProcessing.common.interpolation import InterpolationKind

class MinMaxTimeAlign(unittest.TestCase):
    def setUp(self) -> None:
        sig1 = Signal()
        sig1.time = BufferObject(input_arr=[0, 10, 20, 40, 50], unit='s')
        sig2 = Signal()
        sig2.time = BufferObject(input_arr=[30, 50], unit='s')
        sig3 = Signal()
        sig3.time = BufferObject(input_arr=[0, 45], unit='s')
        
        self.signals_set_1 = [sig1, sig2, sig3]

        sig1 = Signal()
        sig1.time = BufferObject(input_arr=[0, 1, 2, 3], unit='s')
        sig2 = Signal()
        sig2.time = BufferObject(input_arr=[1, 2], unit='s')
        sig3 = Signal()
        sig3.time = BufferObject(input_arr=[3, 4, 5, 6], unit='s')
        
        self.signals_set_2 = [sig1, sig2, sig3]
        return super().setUp()
    
    def test_align_1(self):
        time_align(self.signals_set_1, mode=TimeAlignmentMode.UNION, kind=InterpolationKind.LINEAR)
        valid_values = [0,  6, 12, 18, 25, 31, 37, 43, 50]
        for sig in self.signals_set_1:
            for v1, v2 in zip(valid_values, sig.time):
                self.assertEqual(v1, v2)

    def test_align_2(self):
        time_align(self.signals_set_2, mode=TimeAlignmentMode.UNION, kind=InterpolationKind.LINEAR)
        valid_values = [0, 0, 1, 2, 2, 3, 4, 4, 5, 6]
        for sig in self.signals_set_2:
            for v1, v2 in zip(valid_values, sig.time):
                self.assertEqual(v1, v2)