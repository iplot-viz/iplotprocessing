# Description: Tests methods that determine time-resolution.
# Author: Jaswant Sai Panchumarti

import unittest

from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.math.pre_processing.grid_mixing import get_coarsest_time_unit, get_finest_time_unit


class TestTimeResolution(unittest.TestCase):
    def setUp(self) -> None:
        time_units = ['ms', 'M', 'D', 'h', 'ns']
        self.buffers = []
        for unit in time_units:
            buf = BufferObject(unit=unit)
            self.buffers.append(buf)

        return super().setUp()

    def test_coarsest(self):
        test_unit = get_coarsest_time_unit(self.buffers)
        valid_unit = 'M'
        self.assertEqual(test_unit, valid_unit)

    def test_finest(self):
        test_unit = get_finest_time_unit(self.buffers)
        valid_unit = 'ns'
        self.assertEqual(test_unit, valid_unit)
