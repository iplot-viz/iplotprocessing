# Copyright (c) 2020-2025 ITER Organization,
#               CS 90046
#               13067 St Paul Lez Durance Cedex
#               France
# Author IO
#
# This file is part of iplotprocessing module.
# iplotprocessing python module is free software: you can redistribute it and/or modify it under
# the terms of the MIT license.
#
# This file is part of ITER CODAC software.
# For the terms and conditions of redistribution or use of this software
# refer to the file LICENSE located in the top level directory
# of the distribution package
#


# Description: Tests BufferObject with 2D arrays
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core.bobject import BufferObject
import numpy as np


class TestBObject2D(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_object = BufferObject([[1, 2], [3, 4], [5, 6]])

    def test_data_setter_getter(self) -> None:
        self.assertTrue(isinstance(self.test_object, np.ndarray))
        self.assertEqual(self.test_object.size, 6)
