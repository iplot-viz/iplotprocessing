import unittest
from iplotProcessing.core import PObject
import numpy as np


class PObjectBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_pobject = PObject()

    def test_time(self):
        self.test_pobject.time = [0, 1, 2]
        self.test_pobject.time_unit = "ns"

        self.assertTrue(isinstance(self.test_pobject.time, np.ndarray))
        self.assertEqual(self.test_pobject.time[0], 0)
        self.assertEqual(self.test_pobject.time[1], 1)
        self.assertEqual(self.test_pobject.time[2], 2)
        self.assertEqual(self.test_pobject.time_unit, "ns")
