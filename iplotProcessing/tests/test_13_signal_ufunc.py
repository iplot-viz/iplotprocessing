import unittest
from iplotProcessing.common.time_mixing import TimeAlignmentMode
import numpy as np
from iplotProcessing.core import BufferObject, Signal


class BufferObjectUfunc(unittest.TestCase):
    def setUp(self) -> None:
        self.s1 = Signal()
        self.s1._mixing_mode = TimeAlignmentMode.UNION # Intersection would result in nan's for this closely spaced data.
        self.s1.time = BufferObject([0, 1, 2, 3])
        self.s1.data = BufferObject([0, 1, 2, 3])
        self.s2 = Signal()
        self.s2._mixing_mode = TimeAlignmentMode.UNION
        self.s2.time = BufferObject([0, 1, 2, 3])
        self.s2.data = BufferObject([0, 1, 2, 3])
        self.s3 = Signal()
        self.s3._mixing_mode = TimeAlignmentMode.UNION
        self.s3.time = BufferObject([0, 1, 2, 3])
        self.s3.data = BufferObject([0, 1, 2, 3])
        return super().setUp()

    def test_signal_ufunc_simple(self):
        res = self.s1 + self.s2 + self.s3
        self.assertEqual(res.data.tobytes(), b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08@\x00\x00\x00\x00\x00\x00\x18@\x00\x00\x00\x00\x00\x00"@')

    def test_signal_ufunc_advanced_1(self):
        res = np.sin(self.s1)
        self.assertEqual(res.data.tobytes(), b'\x00\x00\x00\x00\x00\x00\x00\x00\xee\x0c\t\x8fT\xed\xea?F\xb4\xd1\xea\xf6\x18\xed?[\xd5\xb6m8\x10\xc2?')

    def test_bo_ufunc_advanced_2(self):
        res = np.sin(self.s1 + self.s2 + self.s3)
        self.assertEqual(res.data.tobytes(), b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00[\xd5\xb6m8\x10\xc2?\xc0\xa2\xb0\x8a\xf1\xe1\xd1\xbf\x91/\x0c6&`\xda?')