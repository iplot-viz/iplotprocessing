import unittest

from iplotProcessing.core import Signal
from iplotProcessing.math.pre_processing.time_mixing import get_coarsest_time_unit, get_finest_time_unit


class TimeResolution(unittest.TestCase):
    def setUp(self) -> None:
        time_units = ['ms', 'M', 'D', 'h', 'ns']
        self.signals = []
        for unit in time_units:
            sig = Signal()
            sig.time_unit = unit
            self.signals.append(sig)

        return super().setUp()

    def test_coarsest(self):
        test_unit = get_coarsest_time_unit(self.signals)
        valid_unit = 'M'
        self.assertEqual(test_unit, valid_unit)

    def test_finest(self):
        test_unit = get_finest_time_unit(self.signals)
        valid_unit = 'ns'
        self.assertEqual(test_unit, valid_unit)
