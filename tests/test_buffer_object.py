# Description: Unit tests for BufferObject — numpy ndarray subclass with unit tracking.

import numpy as np
import pytest

from iplotProcessing.core.bobject import BufferObject


class TestConstruction:

    def test_no_args_yields_empty_buffer(self):
        buf = BufferObject()
        assert isinstance(buf, np.ndarray)
        assert buf.size == 0
        assert buf.unit == ""

    def test_from_input_array_preserves_values(self):
        buf = BufferObject(input_arr=[1, 2, 3], unit="V")
        assert buf.unit == "V"
        np.testing.assert_array_equal(buf, [1, 2, 3])

    def test_from_shape_creates_uninitialised_buffer(self):
        buf = BufferObject(shape=(3,))
        assert buf.shape == (3,)
        assert buf.unit == ""

    def test_unit_defaults_to_empty_string(self):
        assert BufferObject(input_arr=[1.0]).unit == ""

    def test_zero_dimensional_input_keeps_subclass(self):
        buf = BufferObject(input_arr=np.float64(3.14), unit="s")
        assert isinstance(buf, BufferObject)
        assert buf.unit == "s"


class TestArrayFinalize:

    def test_unit_propagates_through_slicing(self):
        buf = BufferObject(input_arr=[1, 2, 3, 4], unit="A")
        sliced = buf[1:3]
        assert isinstance(sliced, BufferObject)
        assert sliced.unit == "A"

    def test_view_inherits_unit(self):
        buf = BufferObject(input_arr=[1.0, 2.0], unit="kV")
        viewed = buf.view(BufferObject)
        assert viewed.unit == "kV"


class TestUfuncSemantics:

    def test_addition_clears_unit(self):
        a = BufferObject(input_arr=[1, 2, 3], unit="V")
        b = BufferObject(input_arr=[10, 20, 30], unit="V")
        result = a + b
        assert isinstance(result, BufferObject)
        np.testing.assert_array_equal(result, [11, 22, 33])
        assert result.unit == ""

    def test_subtraction_clears_unit(self):
        a = BufferObject(input_arr=[5, 5, 5], unit="m")
        b = BufferObject(input_arr=[1, 2, 3], unit="m")
        result = a - b
        np.testing.assert_array_equal(result, [4, 3, 2])
        assert result.unit == ""

    def test_multiplication_with_scalar_clears_unit(self):
        a = BufferObject(input_arr=[1, 2, 3], unit="V")
        result = a * 2
        np.testing.assert_array_equal(result, [2, 4, 6])
        assert result.unit == ""

    def test_division_with_scalar(self):
        a = BufferObject(input_arr=[2.0, 4.0, 6.0], unit="V")
        result = a / 2
        np.testing.assert_array_almost_equal(result, [1.0, 2.0, 3.0])

    def test_numpy_function_dispatches_through_ufunc(self):
        a = BufferObject(input_arr=[0.0, np.pi / 2, np.pi], unit="rad")
        result = np.sin(a)
        assert isinstance(result, BufferObject)
        np.testing.assert_array_almost_equal(result, [0.0, 1.0, 0.0])
        assert result.unit == ""

    def test_scalar_result_is_wrapped_in_shape_one_buffer(self):
        a = BufferObject(input_arr=[1, 2, 3])
        result = np.sum(a)
        assert isinstance(result, BufferObject)
        assert result.shape == (1,)
        assert result[0] == 6

    def test_zero_dim_result_is_wrapped_in_shape_one_buffer(self):
        a = BufferObject(input_arr=[1.0, 2.0, 3.0])
        result = np.max(a)
        assert isinstance(result, BufferObject)
        assert result.shape == (1,)


class TestReductionWithOut:

    def test_out_parameter_is_unwrapped_to_ndarray(self):
        a = BufferObject(input_arr=[1.0, 2.0, 3.0])
        out = BufferObject(input_arr=np.zeros(3))
        np.add(a, a, out=out)
        np.testing.assert_array_almost_equal(out, [2.0, 4.0, 6.0])


class TestUfuncAtMethod:

    def test_in_place_reduction_returns_none(self):
        buf = BufferObject(input_arr=np.array([1, 2, 3, 4]))
        result = np.add.at(buf, [0, 2], 10)
        assert result is None
        np.testing.assert_array_equal(buf, [11, 2, 13, 4])


class TestCopyAttrsTo:

    def test_view_through_copy_attrs_to_propagates_dict(self):
        a = BufferObject(input_arr=[1, 2, 3], unit="V")
        a.extra = "x"
        target = np.array([4, 5, 6])
        out = a._copy_attrs_to(target)
        assert isinstance(out, BufferObject)
        assert out.unit == "V"
        assert out.extra == "x"
