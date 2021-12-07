# Description: Tests user functions on a Signal
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core import Signal
from iplotProcessing.core.bobject import BufferObject
import numpy as np


def rosenbrock(x, y):
    xv, yv = np.meshgrid(x, y)
    return (1 - xv) ** 2 + 100 * (yv - xv ** 2) ** 2


class TestSignalUserFunc(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.test_signal = Signal()

    def test_ufunc1(self):
        self.test_signal.data_store[0] = BufferObject([0, 1, 2])
        self.test_signal.data_store[1] = BufferObject(
            [0, np.pi * 0.25, np.pi * 0.5])
        self.assertEqual(self.test_signal.rank, 1)

        result = np.sin(self.test_signal)
        self.assertDictEqual(result.alias_map, self.test_signal.alias_map)
        self.assertListEqual(result.data_store[0].tolist(
        ), self.test_signal.data_store[0].tolist())
        self.assertListEqual(result.data_store[1].tolist(), [
                             0., 0.7071067811865475, 1.])

    def test_ufunc2(self):
        self.test_signal.alias_map.clear()
        self.test_signal.alias_map.update(
            {
                'time': {'idx': 0, 'independent': True},
                'dmin': {'idx': 1},
                'dmax': {'idx': 2}
            }
        )
        self.test_signal.data_store[0] = BufferObject([0, 1, 2])
        self.test_signal.data_store[1] = BufferObject(
            [0, np.pi * 0.25, np.pi * 0.5])
        self.test_signal.data_store[2] = BufferObject(
            [0, -np.pi * 0.25, -np.pi * 0.5])
        self.assertEqual(self.test_signal.rank, 2)

        result = np.sin(self.test_signal)
        self.assertDictEqual(result.alias_map, self.test_signal.alias_map)
        self.assertListEqual(result.data_store[0].tolist(
        ), self.test_signal.data_store[0].tolist())
        self.assertListEqual(result.data_store[1].tolist(), [
                             0., 0.7071067811865475, 1.])
        self.assertListEqual(result.data_store[2].tolist(), [
                             0., -0.7071067811865475, -1.])

    def test_ufunc3(self):
        self.test_signal.alias_map.clear()
        self.test_signal.alias_map.update(
            {
                'r': {'idx': 0, 'independent': True},
                'z': {'idx': 1, 'independent': True},
                'psi': {'idx': 2}
            }
        )
        r = np.array([-0.5, -0.2, 0., 0.2, 0.5])
        z = np.array([-1.0, -0.75, -0.5, 0., 0.5, 0.75, 1.0])
        self.test_signal.data_store[0] = BufferObject(r)
        self.test_signal.data_store[1] = BufferObject(z)
        self.test_signal.data_store[2] = rosenbrock(r, z)
        self.assertEqual(self.test_signal.rank, 2)

        result = np.sin(self.test_signal)
        self.assertDictEqual(result.alias_map, self.test_signal.alias_map)
        self.assertListEqual(result.data_store[0].tolist(
        ), self.test_signal.data_store[0].tolist())
        self.assertListEqual(result.data_store[1].tolist(
        ), self.test_signal.data_store[1].tolist())
        self.assertEqual(result.data_store[2].tobytes(
        ),
            b"\x9bW\xc8\x9a|\xa3\xef?\x18\xdd\xac\xd1TJ\xd6?\x8bL8\x91\xfd\xed\xdc?\xc2\x01\xc8\xd2tH\xed?L\x01_\x11\xe5\x86\xe1\xbf\xe3F\x9a\xfd'\xa6\xef?\x19\xd7\xae\x15\x83<\xeb?e\x0f\xb5\x1a\xc6\xa5\xe4?H\xdc\xf8\x99\xad\xb3\xcb?\\\xc3\r\x98\x00\xbf\xd1\xbfk\x7fW\xbf\xfd\xb5\xed?\x13\xd6\xb0=\xbbN\xe7\xbf\x83%\xc3\xfa\xe0f\xe8?wz\xb1\xb0\xa8\xf7\xef\xbf\x84P_\xa0v\xe8\xa8\xbf\xfc\xd9_\xd84\x8d\xe9?\xc5B\xe0\xc7\x81\xfc\xef?\xee\x0c\t\x8fT\xed\xea?\xce\xfe\xbf\xc2\x94\xf4\xe6?<\xcb\xc6@\r\x89\xcb?\xfc\xd9_\xd84\x8d\xe9?\xcb\x0b\x0e\x087M\xe2\xbf\x83%\xc3\xfa\xe0f\xe8?b\xcc\x9b\xbf{Q\xc8?<\xcb\xc6@\r\x89\xcb?\xe3\x95\xe0\x04\xfcV\xeb?\x8d\x01\xfa\x95:\xff\xef?e\x0f\xb5\x1a\xc6\xa5\xe4?UL\x9a\xf1\x83\x9b\xe6?\r{\xd5\x9d\x12\xf3\xbd?k\x7fW\xbf\xfd\xb5\xed?\x86]\x91\xca1O\xe3\xbf\x8bL8\x91\xfd\xed\xdc?\xe6\xf3+\xc8\x17\xc2\xef\xbf\x84P_\xa0v\xe8\xa8\xbf")
