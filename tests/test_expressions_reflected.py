# Description: Unit tests for the reflected expression operators (operands swapped before forwarding).

import numpy as np

from iplotProcessing.math.expressions import reflected


class TestArithmetic:

    def test_add_swaps_operands(self):
        np.testing.assert_array_equal(reflected.add(np.array([1, 2, 3]), 10), [11, 12, 13])

    def test_sub_computes_other_minus_obj(self):
        np.testing.assert_array_equal(reflected.sub(np.array([1, 2, 3]), 10), [9, 8, 7])

    def test_mul_swaps_operands(self):
        np.testing.assert_array_equal(reflected.mul(np.array([1, 2, 3]), 4), [4, 8, 12])

    def test_truediv_computes_other_over_obj(self):
        np.testing.assert_array_almost_equal(reflected.truediv(np.array([2.0, 4.0, 8.0]), 16), [8.0, 4.0, 2.0])

    def test_floordiv_computes_other_floordiv_obj(self):
        np.testing.assert_array_equal(reflected.floordiv(np.array([3, 5, 7]), 20), [6, 4, 2])

    def test_mod_computes_other_mod_obj(self):
        np.testing.assert_array_equal(reflected.mod(np.array([3, 5, 7]), 20), [2, 0, 6])

    def test_div_mod_swaps_operands(self):
        q, r = reflected.div_mod(np.array([3, 5, 7]), 20)
        np.testing.assert_array_equal(q, [6, 4, 2])
        np.testing.assert_array_equal(r, [2, 0, 6])

    def test_power_computes_other_to_obj(self):
        np.testing.assert_array_equal(reflected.power(np.array([2, 3, 4]), 2), [4, 8, 16])

    def test_matmul_swaps_operands(self):
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        np.testing.assert_array_equal(reflected.matmul(b, a), [[19, 22], [43, 50]])


class TestBitwise:

    def test_lshift_swaps_operands(self):
        np.testing.assert_array_equal(reflected.lshift(np.array([1, 2, 3]), 1), [2, 4, 8])

    def test_rshift_swaps_operands(self):
        np.testing.assert_array_equal(reflected.rshift(np.array([1, 2, 3]), 16), [8, 4, 2])


class TestLogical:

    def test_logical_and_is_commutative(self):
        a = np.array([True, False])
        b = np.array([True, True])
        np.testing.assert_array_equal(reflected.logical_and(a, b), [True, False])

    def test_logical_or_is_commutative(self):
        a = np.array([True, False])
        b = np.array([False, False])
        np.testing.assert_array_equal(reflected.logical_or(a, b), [True, False])

    def test_logical_xor_is_commutative(self):
        a = np.array([True, False])
        b = np.array([True, True])
        np.testing.assert_array_equal(reflected.logical_xor(a, b), [False, True])
