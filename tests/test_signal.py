# Description: Unit tests for Signal — multi-dimensional buffer container with alias map.

import numpy as np
import pytest

from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.core.signal import Signal


class TestConstruction:

    def test_default_data_store_has_three_empty_buffers(self):
        s = Signal()
        assert len(s.data_store) == 3
        for buf in s.data_store:
            assert isinstance(buf, BufferObject)
            assert buf.size == 0

    def test_default_alias_map_has_time_and_data(self):
        s = Signal()
        assert s.alias_map == {
            "time": {"idx": 0, "independent": True},
            "data": {"idx": 1},
        }


class TestAccessorClassification:

    def test_independent_accessors_lists_only_independent_indices(self):
        s = Signal()
        assert s.independent_accessors == [0]

    def test_dependent_accessors_lists_only_dependent_indices(self):
        s = Signal()
        assert s.dependent_accessors == [1]

    def test_custom_alias_map_with_two_independents(self):
        s = Signal()
        s._alias_map = {
            "r": {"idx": 0, "independent": True},
            "z": {"idx": 1, "independent": True},
            "psi": {"idx": 2},
        }
        assert s.independent_accessors == [0, 1]
        assert s.dependent_accessors == [2]


class TestAliasGetattr:

    def test_alias_map_resolves_to_data_store_entry(self, simple_signal):
        np.testing.assert_array_equal(simple_signal.data, [10.0, 20.0, 30.0, 40.0])

    def test_unknown_attribute_raises(self):
        s = Signal()
        with pytest.raises(AttributeError):
            _ = s.nonexistent

    def test_envelope_alias_map_exposes_dmin_dmax_davg(self, envelope_signal):
        np.testing.assert_array_equal(envelope_signal.dmin, [0.0, 0.0, 0.0])
        np.testing.assert_array_equal(envelope_signal.dmax, [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(envelope_signal.davg, [0.5, 1.0, 1.5])


class TestRank:

    def test_rank_for_default_one_dim_dependent(self, simple_signal):
        assert simple_signal.rank == 1

    def test_rank_sums_dimensionality_of_dependents(self):
        s = Signal()
        s.data_store[1] = BufferObject(input_arr=np.zeros((4, 5)))
        assert s.rank == 2


class TestUfuncOnSignal:

    def test_unary_sin_preserves_independent_axis(self, simple_signal):
        result = np.sin(simple_signal)
        np.testing.assert_array_equal(result.data_store[0], simple_signal.data_store[0])

    def test_unary_sin_clears_dependent_unit(self, simple_signal):
        result = np.sin(simple_signal)
        assert result.data_store[1].unit == ""

    def test_two_signal_addition_via_ufunc(self, simple_signal, buffer_factory):
        other = Signal()
        other.data_store[0] = buffer_factory([0.0, 1.0, 2.0, 3.0], unit="s")
        other.data_store[1] = buffer_factory([1.0, 2.0, 3.0, 4.0], unit="V")
        result = np.add(simple_signal, other)
        np.testing.assert_array_equal(result.data_store[1], [11.0, 22.0, 33.0, 44.0])
        np.testing.assert_array_equal(result.data_store[0], simple_signal.data_store[0])

    def test_result_signal_keeps_alias_map(self, simple_signal):
        result = np.negative(simple_signal)
        assert result.alias_map == simple_signal.alias_map


class TestArithmeticOperators:

    def test_signal_plus_signal(self, simple_signal, buffer_factory):
        other = Signal()
        other.data_store[0] = buffer_factory([0.0, 1.0, 2.0, 3.0], unit="s")
        other.data_store[1] = buffer_factory([5.0, 5.0, 5.0, 5.0], unit="V")
        out = simple_signal + other
        np.testing.assert_array_equal(out.data_store[1], [15.0, 25.0, 35.0, 45.0])

    def test_signal_minus_signal(self, simple_signal, buffer_factory):
        other = Signal()
        other.data_store[0] = buffer_factory([0.0, 1.0, 2.0, 3.0], unit="s")
        other.data_store[1] = buffer_factory([1.0, 2.0, 3.0, 4.0], unit="V")
        out = simple_signal - other
        np.testing.assert_array_equal(out.data_store[1], [9.0, 18.0, 27.0, 36.0])

    def test_signal_times_scalar(self, simple_signal):
        out = simple_signal * 2
        np.testing.assert_array_equal(out.data_store[1], [20.0, 40.0, 60.0, 80.0])

    def test_signal_divided_by_scalar(self, simple_signal):
        out = simple_signal / 2
        np.testing.assert_array_almost_equal(out.data_store[1], [5.0, 10.0, 15.0, 20.0])

    def test_signal_modulo_scalar(self, simple_signal):
        out = simple_signal % 7
        np.testing.assert_array_equal(out.data_store[1], [3.0, 6.0, 2.0, 5.0])

    def test_signal_power(self, simple_signal):
        s = Signal()
        s.data_store[0] = simple_signal.data_store[0]
        s.data_store[1] = BufferObject(input_arr=[1.0, 2.0, 3.0, 4.0])
        out = s ** 2
        np.testing.assert_array_almost_equal(out.data_store[1], [1.0, 4.0, 9.0, 16.0])

    def test_negation(self, simple_signal):
        out = -simple_signal
        np.testing.assert_array_equal(out.data_store[1], [-10.0, -20.0, -30.0, -40.0])

    def test_absolute_value(self):
        s = Signal()
        s.data_store[0] = BufferObject(input_arr=[0.0, 1.0])
        s.data_store[1] = BufferObject(input_arr=[-3.0, 4.0])
        out = abs(s)
        np.testing.assert_array_equal(out.data_store[1], [3.0, 4.0])


class TestUfuncWithOutParameter:

    def test_ufunc_with_out_signal_writes_in_place(self, simple_signal, buffer_factory):
        other = Signal()
        other.data_store[0] = buffer_factory([0.0, 1.0, 2.0, 3.0], unit="s")
        other.data_store[1] = buffer_factory([1.0, 2.0, 3.0, 4.0], unit="V")
        target = Signal()
        target.data_store[0] = buffer_factory([0.0, 1.0, 2.0, 3.0], unit="s")
        target.data_store[1] = buffer_factory([0.0, 0.0, 0.0, 0.0], unit="V")
        np.add(simple_signal, other, out=target)
        np.testing.assert_array_equal(target.data_store[1], [11.0, 22.0, 33.0, 44.0])


class TestReflectedOperators:

    def test_scalar_plus_signal(self, simple_signal):
        out = 100 + simple_signal
        np.testing.assert_array_equal(out.data_store[1], [110.0, 120.0, 130.0, 140.0])

    def test_scalar_minus_signal(self, simple_signal):
        out = 100 - simple_signal
        np.testing.assert_array_equal(out.data_store[1], [90.0, 80.0, 70.0, 60.0])

    def test_scalar_times_signal(self, simple_signal):
        out = 3 * simple_signal
        np.testing.assert_array_equal(out.data_store[1], [30.0, 60.0, 90.0, 120.0])

    def test_scalar_divided_by_signal(self):
        s = Signal()
        s.data_store[0] = BufferObject(input_arr=[0.0, 1.0])
        s.data_store[1] = BufferObject(input_arr=[2.0, 4.0])
        out = 8 / s
        np.testing.assert_array_almost_equal(out.data_store[1], [4.0, 2.0])
