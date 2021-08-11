import unittest
from iplotProcessing.core import PObject
import numpy as np


class PObjectBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_pobject = PObject()

    def test_secondary_dobject(self):
        self.test_pobject.data_secondary = [0, 1, 2]
        self.test_pobject.data_secondary_unit = "m"
        self.assertTrue(isinstance(self.test_pobject.data_secondary, np.ndarray))
        self.assertEqual(self.test_pobject.data_secondary[0], 0)
        self.assertEqual(self.test_pobject.data_secondary[1], 1)
        self.assertEqual(self.test_pobject.data_secondary[2], 2)
        self.assertEqual(self.test_pobject.data_secondary_unit, "m")
