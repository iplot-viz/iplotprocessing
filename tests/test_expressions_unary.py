# Description: Unit tests for the unary expression operators.

import numpy as np

from iplotProcessing.math.expressions import unary


class TestUnary:

    def test_neg_inverts_sign(self):
        np.testing.assert_array_equal(unary.neg(np.array([1, -2, 3])), [-1, 2, -3])

    def test_neg_on_scalar(self):
        assert unary.neg(5) == -5

    def test_absolute_returns_positive_values(self):
        np.testing.assert_array_equal(unary.absolute(np.array([-1, -2, 3])), [1, 2, 3])

    def test_absolute_on_floats(self):
        np.testing.assert_array_almost_equal(unary.absolute(np.array([-1.5, 2.5])), [1.5, 2.5])

    def test_invert_flips_bits_for_integers(self):
        np.testing.assert_array_equal(unary.invert(np.array([0, 1, 2], dtype=np.uint8)), [255, 254, 253])

    def test_invert_negates_booleans(self):
        np.testing.assert_array_equal(unary.invert(np.array([True, False, True])), [False, True, False])
