import unittest
from iplotProcessing.core import PObject
import numpy as np


class PObjectBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_pobject = PObject()

    def test_primary_dobject_direct(self):
        self.test_pobject.data_primary = [0, 1, 2]
        self.test_pobject.data_primary_unit = "m"

        self.assertTrue(isinstance(self.test_pobject.data_primary, np.ndarray))
        self.assertEqual(self.test_pobject.data_primary[0], 0)
        self.assertEqual(self.test_pobject.data_primary[1], 1)
        self.assertEqual(self.test_pobject.data_primary[2], 2)
        self.assertEqual(self.test_pobject.data_unit, "m")
