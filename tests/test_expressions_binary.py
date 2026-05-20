# Description: Unit tests for the binary expression operators (forward to numpy).

import numpy as np
import pytest

from iplotProcessing.math.expressions import binary


@pytest.fixture
def lhs():
    return np.array([10, 20, 30])


@pytest.fixture
def rhs():
    return np.array([1, 2, 3])


class TestArithmetic:

    def test_add(self, lhs, rhs):
        np.testing.assert_array_equal(binary.add(lhs, rhs), [11, 22, 33])

    def test_sub(self, lhs, rhs):
        np.testing.assert_array_equal(binary.sub(lhs, rhs), [9, 18, 27])

    def test_mul(self, lhs, rhs):
        np.testing.assert_array_equal(binary.mul(lhs, rhs), [10, 40, 90])

    def test_truediv(self, lhs, rhs):
        np.testing.assert_array_almost_equal(binary.truediv(lhs, rhs), [10.0, 10.0, 10.0])

    def test_floordiv(self):
        np.testing.assert_array_equal(binary.floordiv(np.array([7, 8, 9]), 2), [3, 4, 4])

    def test_mod(self):
        np.testing.assert_array_equal(binary.mod(np.array([7, 8, 9]), 3), [1, 2, 0])

    def test_div_mod_returns_quotient_and_remainder(self):
        q, r = binary.div_mod(np.array([7, 8, 9]), 3)
        np.testing.assert_array_equal(q, [2, 2, 3])
        np.testing.assert_array_equal(r, [1, 2, 0])

    def test_power(self):
        np.testing.assert_array_equal(binary.power(np.array([2, 3, 4]), 2), [4, 9, 16])

    def test_matmul(self):
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        np.testing.assert_array_equal(binary.matmul(a, b), [[19, 22], [43, 50]])


class TestBitwise:

    def test_lshift(self):
        np.testing.assert_array_equal(binary.lshift(np.array([1, 2, 3]), 1), [2, 4, 6])

    def test_rshift(self):
        np.testing.assert_array_equal(binary.rshift(np.array([4, 8, 16]), 1), [2, 4, 8])


class TestLogical:

    def test_logical_and(self):
        a = np.array([True, True, False, False])
        b = np.array([True, False, True, False])
        np.testing.assert_array_equal(binary.logical_and(a, b), [True, False, False, False])

    def test_logical_or(self):
        a = np.array([True, True, False, False])
        b = np.array([True, False, True, False])
        np.testing.assert_array_equal(binary.logical_or(a, b), [True, True, True, False])

    def test_logical_xor(self):
        a = np.array([True, True, False, False])
        b = np.array([True, False, True, False])
        np.testing.assert_array_equal(binary.logical_xor(a, b), [False, True, True, False])
