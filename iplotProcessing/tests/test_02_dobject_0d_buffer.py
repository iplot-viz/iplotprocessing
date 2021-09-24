# Description: Tests BufferObject
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core.bobject import BufferObject
import numpy as np


class DObjectTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_object = BufferObject(1)

    def test_data_setter_getter(self) -> None:
        self.assertTrue(isinstance(self.test_object, np.ndarray))
        self.assertEqual(self.test_object.size, 1)

    def test_unit_attrib(self) -> None:
        self.test_object.unit = "ns"
        self.assertEqual(self.test_object.unit, "ns")
