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


# Description: Tests all the binary mathematical operators and functions.
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core import BufferObject, Signal


class TestSignal2DAdd(unittest.TestCase):
    def setUp(self) -> None:
        self.signal = Signal()
        self.signal.data_store[0] = BufferObject([1, 2, 3, 4, 5])
        self.signal.data_store[1] = BufferObject([1, 2, 3, 4, 5])
        return super().setUp()

    def test_regular_1(self):
        s = Signal()
        s.data_store[0] = self.signal.data_store[0]
        s.data_store[1] = self.signal.data_store[1]
        result = s + self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x02\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00'
                         b'\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s - self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s * self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00'
                         b'\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s @ self.signal
        self.assertEqual(result.data.tobytes(),
                         b'7\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s / self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00'
                         b'\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf0?')
        # print(result.data, result.data.tobytes())

        result = s // self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s % self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result1, result2 = divmod(s, self.signal)
        self.assertEqual(result1.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result1.data, result1.data.tobytes())
        self.assertEqual(result2.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result2.data, result2.data.tobytes())

        result = s ** self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x005\x0c\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s << self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x02\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00'
                         b'\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\xa0\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s >> self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s & self.signal
        self.assertEqual(result.data.tobytes(), b'\x01\x01\x01\x01\x01')
        # print(result.data, result.data.tobytes())

        result = s ^ self.signal
        self.assertEqual(result.data.tobytes(), b'\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = s | self.signal
        self.assertEqual(result.data.tobytes(), b'\x01\x01\x01\x01\x01')
        # print(result.data, result.data.tobytes())

    def test_reflected(self):
        result = 4 + self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x05\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00'
                         b'\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 - self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x03\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff')
        # print(result.data, result.data.tobytes())

        result = 4 * self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x04\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00'
                         b'\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 / self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x10@\x00\x00\x00\x00\x00\x00\x00@UUUUUU\xf5?'
                         b'\x00\x00\x00\x00\x00\x00\xf0?\x9a\x99\x99\x99\x99\x99\xe9?')
        # print(result.data, result.data.tobytes())

        result = 4 // self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x04\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 % self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result1, result2 = divmod(4, self.signal)
        self.assertEqual(result1.data.tobytes(),
                         b'\x04\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result1.data, result1.data.tobytes())
        self.assertEqual(result2.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00')
        # print(result2.data, result2.data.tobytes())

        result = 4 ** self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x04\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 << self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x08\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00'
                         b'\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 >> self.signal
        self.assertEqual(result.data.tobytes(),
                         b'\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 & self.signal
        self.assertEqual(result.data.tobytes(), b'\x01\x01\x01\x01\x01')
        # print(result.data, result.data.tobytes())

        result = 4 ^ self.signal
        self.assertEqual(result.data.tobytes(), b'\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = 4 | self.signal
        self.assertEqual(result.data.tobytes(), b'\x01\x01\x01\x01\x01')
        # print(result.data, result.data.tobytes())

    def test_regular_2(self):
        result = self.signal + 4
        self.assertEqual(result.data.tobytes(),
                         b'\x05\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00'
                         b'\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\t\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal - 4
        self.assertEqual(result.data.tobytes(),
                         b'\xfd\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                         b'\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal * 4
        self.assertEqual(result.data.tobytes(),
                         b'\x04\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00'
                         b'\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal / 4
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\xd0?\x00\x00\x00\x00\x00\x00\xe0?\x00\x00\x00\x00\x00\x00'
                         b'\xe8?\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\xf4?')
        # print(result.data, result.data.tobytes())

        result = self.signal // 4
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal % 4
        self.assertEqual(result.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result1, result2 = divmod(self.signal, 4)
        self.assertEqual(result1.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result1.data, result1.data.tobytes())
        self.assertEqual(result2.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00')
        # print(result2.data, result2.data.tobytes())

        result = self.signal ** 4
        self.assertEqual(result.data.tobytes(),
                         b'\x01\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00Q\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00q\x02\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal << 4
        self.assertEqual(result.data.tobytes(),
                         b'\x10\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x00\x00'
                         b'\x00\x00@\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal >> 4
        self.assertEqual(result.data.tobytes(),
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal & 4
        self.assertEqual(result.data.tobytes(), b'\x01\x01\x01\x01\x01')
        # print(result.data, result.data.tobytes())

        result = self.signal ^ 4
        self.assertEqual(result.data.tobytes(), b'\x00\x00\x00\x00\x00')
        # print(result.data, result.data.tobytes())

        result = self.signal | 4
        self.assertEqual(result.data.tobytes(), b'\x01\x01\x01\x01\x01')
        # print(result.data, result.data.tobytes())


if __name__ == "__main__":
    unittest.main()
