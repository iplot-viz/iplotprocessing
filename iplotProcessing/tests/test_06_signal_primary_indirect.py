# Description: Tests Signal attributes
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.example.emulatedDataAccess import SignalAdapterStub
import numpy as np


class SignalBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_signal = SignalAdapterStub()

    def test_primary_dobject_indirect(self):
        self.test_signal.data_primary = [0, 1, 2]
        self.test_signal.data_unit = "m"

        self.assertTrue(isinstance(self.test_signal.data_primary, np.ndarray))
        self.assertEqual(self.test_signal.data[0], 0)
        self.assertEqual(self.test_signal.data[1], 1)
        self.assertEqual(self.test_signal.data[2], 2)
        self.assertEqual(self.test_signal.data_unit, "m")
