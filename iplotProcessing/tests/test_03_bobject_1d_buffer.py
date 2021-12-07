# Description: Tests BufferObject with 1D arrays
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core.bobject import BufferObject
import numpy as np


class TestBObject1D(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_object = BufferObject([1, 2])

    def test_data_setter_getter(self) -> None:
        self.assertTrue(isinstance(self.test_object, np.ndarray))
        self.assertEqual(self.test_object.size, 2)
