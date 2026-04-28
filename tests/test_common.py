# Description: Unit tests for the common subpackage (errors, units, enums).

import pytest

from iplotProcessing.common import (
    DATE,
    DATE_TIME,
    DATE_TIME_PRECISE,
    PRECISE_TIME,
    TIME,
    InvalidExpression,
    InvalidNDims,
    InvalidVariable,
)
from iplotProcessing.common.grid_mixing import GridAlignmentMode
from iplotProcessing.common.interpolation import InterpolationKind


class TestUnitConstants:

    def test_date_units_in_order(self):
        assert DATE == ['Y', 'M', 'W', 'D']

    def test_time_units_in_order(self):
        assert TIME == ['h', 'm', 's']

    def test_precise_time_units_in_order(self):
        assert PRECISE_TIME == ['ms', 'us', 'ns']

    def test_date_time_concatenates_date_and_time(self):
        assert DATE_TIME == DATE + TIME

    def test_date_time_precise_concatenates_all_three(self):
        assert DATE_TIME_PRECISE == DATE + TIME + PRECISE_TIME

    def test_precise_time_is_ordered_coarsest_to_finest(self):
        assert DATE_TIME_PRECISE.index('ms') < DATE_TIME_PRECISE.index('us') < DATE_TIME_PRECISE.index('ns')


class TestGridAlignmentMode:

    def test_intersection_value(self):
        assert GridAlignmentMode.INTERSECTION == "intersection"

    def test_union_value(self):
        assert GridAlignmentMode.UNION == "union"


class TestInterpolationKind:

    def test_known_values(self):
        assert InterpolationKind.LINEAR == 'linear'
        assert InterpolationKind.NEAREST == 'nearest'
        assert InterpolationKind.NEAREST_UP == 'nearest-up'
        assert InterpolationKind.ZERO == 'zero'
        assert InterpolationKind.SLINEAR == 'slinear'
        assert InterpolationKind.QUADRATIC == 'quadratic'
        assert InterpolationKind.CUBIC == 'cubic'
        assert InterpolationKind.PREVIOUS == 'previous'
        assert InterpolationKind.NEXT == 'next'


class TestInvalidExpression:

    def test_is_an_exception(self):
        assert issubclass(InvalidExpression, Exception)

    def test_can_be_raised_with_message(self):
        with pytest.raises(InvalidExpression, match="boom"):
            raise InvalidExpression("boom")


class TestInvalidNDims:

    def test_is_an_exception(self):
        assert issubclass(InvalidNDims, Exception)

    def test_can_be_raised_with_payload(self):
        with pytest.raises(InvalidNDims):
            raise InvalidNDims(3)


class TestInvalidVariable:

    def test_collects_keys_missing_from_locals(self):
        var_map = {"key0": "x", "key1": "y", "key2": "z"}
        locals_ = {"key0": 1, "key2": 3}
        err = InvalidVariable(var_map, locals_)
        assert err.invalid_keys == {"key1"}

    def test_no_missing_keys_when_all_defined(self):
        var_map = {"key0": "x"}
        locals_ = {"key0": 1}
        err = InvalidVariable(var_map, locals_)
        assert err.invalid_keys == set()

    def test_str_representation_lists_invalid_keys(self):
        var_map = {"key0": "x", "key1": "y"}
        locals_ = {"key0": 1}
        err = InvalidVariable(var_map, locals_)
        assert "key1" in str(err)
        assert "undefined" in str(err)
