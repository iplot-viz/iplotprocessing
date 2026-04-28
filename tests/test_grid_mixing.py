# Description: Unit tests for grid_mixing — signal alignment, union, intersection helpers.

import numpy as np
import pytest

from iplotProcessing.common.errors import InvalidNDims
from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.math.pre_processing.grid_mixing import (
    _check_alias_map_equal,
    _get_common_num_dims,
    get_coarsest_time_unit,
    get_finest_time_unit,
    intersection,
    union,
)


@pytest.fixture
def buf():
    def _make(values, unit=""):
        return BufferObject(input_arr=np.asarray(values), unit=unit)
    return _make


class TestCheckAliasMapEqual:

    def test_returns_true_for_identical_alias_maps(self):
        from iplotProcessing.core.signal import Signal
        a, b = Signal(), Signal()
        assert _check_alias_map_equal([a, b]) is True

    def test_returns_false_when_alias_maps_differ(self):
        from iplotProcessing.core.signal import Signal
        a = Signal()
        b = Signal()
        b._alias_map = {"r": {"idx": 0, "independent": True}, "data": {"idx": 1}}
        assert _check_alias_map_equal([a, b]) is False

    def test_single_signal_is_trivially_equal(self):
        from iplotProcessing.core.signal import Signal
        assert _check_alias_map_equal([Signal()]) is True


class TestGetCommonNumDims:

    def test_uniform_dims_returns_ndim(self):
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        assert _get_common_num_dims([a, b]) == 1

    def test_mismatched_dims_returns_minus_one(self):
        a = np.array([1, 2, 3])
        b = np.array([[1, 2], [3, 4]])
        assert _get_common_num_dims([a, b]) == -1


class TestUnion:

    def test_returns_sorted_unique_values(self, buf):
        a = buf([0.0, 1.0, 2.0])
        b = buf([1.5, 2.0, 2.5])
        out = union([a, b])
        np.testing.assert_array_almost_equal(out, [0.0, 1.0, 1.5, 2.0, 2.5])

    def test_returns_buffer_object(self, buf):
        out = union([buf([1, 2]), buf([3, 4])])
        assert isinstance(out, BufferObject)

    def test_empty_input_returns_none(self):
        assert union([]) is None

    def test_mismatched_dimensions_returns_none(self, buf):
        a = buf([1, 2, 3])
        b = buf([[1, 2], [3, 4]])
        assert union([a, b]) is None

    def test_two_dimensional_input_raises_invalid_ndims(self, buf):
        a = buf([[1, 2], [3, 4]])
        b = buf([[5, 6], [7, 8]])
        with pytest.raises(InvalidNDims):
            union([a, b])

    def test_promotes_to_float_when_any_input_is_float(self, buf):
        out = union([buf([1, 2, 3]), buf([1.5, 2.5])])
        assert "float" in str(out.dtype)


class TestIntersection:

    def test_returns_linspace_between_overlapping_bounds(self, buf):
        a = buf([0.0, 1.0, 2.0, 3.0])
        b = buf([1.0, 2.0, 3.0, 4.0])
        out = intersection([a, b])
        assert isinstance(out, BufferObject)
        assert out[0] == 1.0
        assert out[-1] == 3.0

    def test_empty_input_returns_none(self):
        assert intersection([]) is None

    def test_mismatched_dimensions_returns_none(self, buf):
        a = buf([1, 2, 3])
        b = buf([[1, 2], [3, 4]])
        assert intersection([a, b]) is None

    def test_two_dimensional_input_raises_invalid_ndims(self, buf):
        a = buf([[1, 2], [3, 4]])
        b = buf([[5, 6], [7, 8]])
        with pytest.raises(InvalidNDims):
            intersection([a, b])

    def test_promotes_to_float_when_any_input_is_float(self, buf):
        a = buf([0, 5, 10])
        b = buf([2.0, 7.0])
        out = intersection([a, b])
        assert "float" in str(out.dtype)


class TestTimeUnitHelpers:

    def test_get_finest_time_unit_picks_ns_over_ms(self, buf):
        out = get_finest_time_unit([buf([1, 2], unit="ms"), buf([3, 4], unit="ns")])
        assert out == "ns"

    def test_get_finest_time_unit_handles_unknown_unit(self, buf):
        out = get_finest_time_unit([buf([1, 2], unit="unknown")])
        assert out == "ns"

    def test_get_coarsest_time_unit_picks_ms_over_ns(self, buf):
        out = get_coarsest_time_unit([buf([1, 2], unit="ms"), buf([3, 4], unit="ns")])
        assert out == "ms"

    def test_get_coarsest_time_unit_with_only_seconds(self, buf):
        out = get_coarsest_time_unit([buf([1, 2], unit="s")])
        assert out == "s"

    def test_get_coarsest_time_unit_skips_arrays_without_unit_attr(self):
        plain = np.array([1, 2, 3])
        out = get_coarsest_time_unit([plain])
        assert out == "ns"
