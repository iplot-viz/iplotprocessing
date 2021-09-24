# Description: Tests Signal attributes
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core import Signal
import numpy as np


class SignalBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_signal = Signal()

    def test_primary_dobject_mixed1(self):
        self.test_signal.data_primary = [0, 1, 2]
        self.test_signal.data_primary_unit = "m"

        self.assertTrue(isinstance(self.test_signal.data_primary, np.ndarray))
        self.assertEqual(self.test_signal.data_primary[0], 0)
        self.assertEqual(self.test_signal.data_primary[1], 1)
        self.assertEqual(self.test_signal.data_primary[2], 2)
        self.assertEqual(self.test_signal.data_unit, "m")
