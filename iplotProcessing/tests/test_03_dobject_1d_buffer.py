import unittest
from iplotProcessing.core.dobject import DObject
import numpy as np


class DObjectTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_object = DObject()

    def test_data_setter_getter(self) -> None:
        self.test_object.buffer = [1, 2]
        self.assertTrue(isinstance(self.test_object.buffer, np.ndarray))
        self.assertEqual(self.test_object.size, 2)
