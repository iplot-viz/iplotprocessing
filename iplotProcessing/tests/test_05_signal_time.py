import unittest
from iplotProcessing.core import Signal
import numpy as np


class SignalBasicTesting(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_signal = Signal()

    def test_time(self):
        self.test_signal.time = [0, 1, 2]
        self.test_signal.time_unit = "ns"

        self.assertTrue(isinstance(self.test_signal.time, np.ndarray))
        self.assertEqual(self.test_signal.time[0], 0)
        self.assertEqual(self.test_signal.time[1], 1)
        self.assertEqual(self.test_signal.time[2], 2)
        self.assertEqual(self.test_signal.time_unit, "ns")
