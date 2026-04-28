# Description: Unit tests for the augmented expression operators (delegate to dunder methods).

import numpy as np
import pytest

from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.math.expressions import augmented


@pytest.fixture
def lhs():
    return BufferObject(input_arr=[10, 20, 30])


@pytest.fixture
def rhs():
    return BufferObject(input_arr=[1, 2, 3])


class TestArithmetic:

    def test_add(self, lhs, rhs):
        np.testing.assert_array_equal(augmented.add(lhs, rhs), [11, 22, 33])

    def test_sub(self, lhs, rhs):
        np.testing.assert_array_equal(augmented.sub(lhs, rhs), [9, 18, 27])

    def test_mul(self, lhs, rhs):
        np.testing.assert_array_equal(augmented.mul(lhs, rhs), [10, 40, 90])

    def test_truediv(self, lhs, rhs):
        np.testing.assert_array_almost_equal(augmented.truediv(lhs, rhs), [10.0, 10.0, 10.0])

    def test_floordiv(self):
        a = BufferObject(input_arr=[7, 8, 9])
        np.testing.assert_array_equal(augmented.floordiv(a, 2), [3, 4, 4])

    def test_mod(self):
        a = BufferObject(input_arr=[7, 8, 9])
        np.testing.assert_array_equal(augmented.mod(a, 3), [1, 2, 0])

    def test_div_mod(self):
        a = BufferObject(input_arr=[7, 8, 9])
        q, r = augmented.div_mod(a, 3)
        np.testing.assert_array_equal(q, [2, 2, 3])
        np.testing.assert_array_equal(r, [1, 2, 0])

    def test_power(self):
        a = BufferObject(input_arr=[2, 3, 4])
        np.testing.assert_array_equal(augmented.power(a, 2), [4, 9, 16])

    def test_matmul(self):
        a = BufferObject(input_arr=[[1, 2], [3, 4]])
        b = BufferObject(input_arr=[[5, 6], [7, 8]])
        np.testing.assert_array_equal(augmented.matmul(a, b), [[19, 22], [43, 50]])


class TestBitwise:

    def test_lshift(self):
        a = BufferObject(input_arr=[1, 2, 3])
        np.testing.assert_array_equal(augmented.lshift(a, 1), [2, 4, 6])

    def test_rshift_is_broken_in_production(self):
        # NOTE: augmented.rshift currently calls obj.__rshift____ (four trailing underscores)
        # which raises AttributeError. This test documents the broken state — do not fix
        # without a coordinated change. See: iplotProcessing/math/expressions/augmented.py:56
        a = BufferObject(input_arr=[4, 8, 16])
        with pytest.raises(AttributeError):
            augmented.rshift(a, 1)


class TestLogical:

    def test_logical_and(self):
        a = BufferObject(input_arr=[True, True, False, False])
        b = BufferObject(input_arr=[True, False, True, False])
        np.testing.assert_array_equal(augmented.logical_and(a, b), [True, False, False, False])

    def test_logical_or(self):
        a = BufferObject(input_arr=[True, True, False, False])
        b = BufferObject(input_arr=[True, False, True, False])
        np.testing.assert_array_equal(augmented.logical_or(a, b), [True, True, True, False])

    def test_logical_xor(self):
        a = BufferObject(input_arr=[True, True, False, False])
        b = BufferObject(input_arr=[True, False, True, False])
        np.testing.assert_array_equal(augmented.logical_xor(a, b), [False, True, True, False])
