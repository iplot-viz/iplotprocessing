import unittest
from iplotProcessing.core import Signal
import numpy as np


class SignalBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_signal = Signal()

    def test_secondary_dobject(self):
        self.test_signal.data_secondary = [0, 1, 2]
        self.test_signal.data_secondary_unit = "m"
        self.assertTrue(isinstance(self.test_signal.data_secondary, np.ndarray))
        self.assertEqual(self.test_signal.data_secondary[0], 0)
        self.assertEqual(self.test_signal.data_secondary[1], 1)
        self.assertEqual(self.test_signal.data_secondary[2], 2)
        self.assertEqual(self.test_signal.data_secondary_unit, "m")
