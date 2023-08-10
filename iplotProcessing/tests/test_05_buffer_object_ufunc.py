# Description: Tests user functions on a buffer object.
# Author: Jaswant Sai Panchumarti

import unittest
import numpy as np
from iplotProcessing.core import BufferObject


class TestBObjectUserFunc(unittest.TestCase):
    def setUp(self) -> None:
        self.b1 = BufferObject([0, 1, 2, 3], unit='s')
        self.b2 = BufferObject([0, 1, 2, 3], unit='s')
        self.b3 = BufferObject([0, 1, 2, 3], unit='s')
        return super().setUp()

    def test_bo_ufunc_simple(self):
        res = self.b1 + self.b2 + self.b3
        self.assertEqual(res.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00'
                         b'\x06\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00')
        # self.assertEqual(res.unit, 's')

    def test_bo_ufunc_advanced_1(self):
        res = np.sin(self.b1)
        self.assertEqual(res.tobytes(
        ), b'\x00\x00\x00\x00\x00\x00\x00\x00\xee\x0c\t\x8fT\xed\xea?F\xb4\xd1\xea\xf6\x18\xed?[\xd5\xb6m8\x10\xc2?')
        # self.assertEqual(res.unit, 's')

    def test_bo_ufunc_advanced_2(self):
        res = np.sin(self.b1 + self.b2 + self.b3)
        self.assertEqual(res.tobytes(
        ), b'\x00\x00\x00\x00\x00\x00\x00\x00[\xd5\xb6m8\x10\xc2?\xc0\xa2\xb0\x8a\xf1\xe1\xd1\xbf\x91/\x0c6&`\xda?')
        # self.assertEqual(res.unit, 's')
