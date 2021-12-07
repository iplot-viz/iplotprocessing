from scipy.interpolate import interp1d, interp2d
import numpy as np
import typing

from iplotProcessing.common.errors import InvalidNDims
from iplotProcessing.common.interpolation import InterpolationKind
from iplotProcessing.common.grid_mixing import GridAlignmentMode
from iplotProcessing.common.units import DATE_TIME_PRECISE
from iplotProcessing.core import Signal, BufferObject

from iplotLogging import setupLogger as sl

from scipy.interpolate.interpnd import LinearNDInterpolator

logger = sl.get_logger(__name__, "INFO")


def _check_alias_map_equal(signals: typing.List[Signal]) -> bool:
    for sig1, sig2 in zip(signals[:-1], signals[1:]):
        if not (sig1.alias_map == sig2.alias_map):
            return False
    return True

def _get_common_num_dims(arrays: typing.List[np.ndarray]) -> int:
    ar_iterator = iter(arrays)
    ndim = next(ar_iterator).ndim

    for arr in arrays[:-1]:
        ndim = arr.ndim
        if ndim != next(ar_iterator).ndim:
            return -1

    return ndim

def align(signals: typing.List[Signal], mode=GridAlignmentMode.INTERSECTION, kind=InterpolationKind.LINEAR):

    # all signals must have same alias_map.
    if not _check_alias_map_equal(signals):
        return

    num_signals = len(signals)
    indep_ids = signals[0].independent_accessors
    num_independent = len(indep_ids)
    common_bases = [None] * num_independent

    if not num_signals or not num_independent:
        return

    for i in indep_ids:
        i_bases = [sig.data_store[i] for sig in signals]

        if mode == GridAlignmentMode.INTERSECTION:
            common_bases[i] = intersection(i_bases)
        elif mode == GridAlignmentMode.UNION:
            common_bases[i] = union(i_bases)
        else:
            logger.warning(f"Unsupported alignment mode: {mode}")
            return

        if i_bases[0].unit in DATE_TIME_PRECISE:  # handle time units. a little special
            common_bases[i].unit = get_finest_time_unit(i_bases)

    # rebase every signal's dependent array onto the common independent arrays
    for sig in signals:
        try:
            # interpolate from old base
            for i in sig.dependent_accessors:
                if sig.data_store[i].ndim == 1:
                    f = interp1d(
                        sig.data_store[indep_ids[0]], sig.data_store[i], kind=kind, fill_value='extrapolate')
                    if f:
                        dunit = sig.data_store[i].unit
                        sig.data_store[i] = BufferObject(
                            input_arr=f(common_bases[0]), unit=dunit)
                elif sig.data_store[i].ndim == 2:
                    f = interp2d(sig.data_store[indep_ids[1]], sig.data_store[indep_ids[0]],
                                 sig.data_store[i], kind=kind, fill_value='extrapolate')
                    if f:
                        dunit = sig.data_store[i].unit
                        sig.data_store[i] = BufferObject(
                            input_arr=f(common_bases[1], common_bases[0]), unit=dunit)
                elif sig.data_store[i].ndim > 2:
                    indep_vectors = [sig.data_store[i] for i in indep_ids]
                    points = list(zip(*indep_vectors))
                    f = LinearNDInterpolator(
                        points, sig.data_store[i].ravel(), fill_value='extrapolate')
                    if f:
                        dunit = sig.data_store[i].unit
                        new_bases = reversed(common_bases)
                        new_bases = np.meshgrid(*new_bases)
                        sig.data_store[i] = BufferObject(
                            input_arr=f(*new_bases), unit=dunit)

            for i in indep_ids:
                sig.data_store[i] = common_bases[i]

        except AttributeError:
            continue


def get_finest_time_unit(arrays: typing.List[BufferObject]) -> str:
    idx = -1
    for arr in arrays:
        try:
            idx = max(DATE_TIME_PRECISE.index(arr.unit), idx)
        except (ValueError, AttributeError) as _:
            continue

    return DATE_TIME_PRECISE[idx]


def get_coarsest_time_unit(arrays: typing.List[BufferObject]) -> str:
    idx = len(DATE_TIME_PRECISE) - 1
    for arr in arrays:
        try:
            idx = min(DATE_TIME_PRECISE.index(arr.unit), idx)
        except (ValueError, AttributeError) as _:
            continue

    return DATE_TIME_PRECISE[idx]


def intersection(arrays: typing.List[BufferObject]):

    if not len(arrays):
        return

    ndim = _get_common_num_dims(arrays)
    if ndim < 0:
        return

    if ndim == 1:
        num_points = 0
        vmin = np.iinfo(np.int64).min
        vmax = np.iinfo(np.int64).max
        vdtype = np.int64

        for arr in arrays:
            try:
                vmin = max(min(arr), vmin)
                vmax = min(max(arr), vmax)
                num_points = max(arr.size, num_points)
                if 'float' in str(arr.dtype):
                    vdtype = np.float64
            except AttributeError:
                continue

        return np.linspace(vmin, vmax, num_points + 1, dtype=vdtype).view(BufferObject)
    else:
        raise InvalidNDims(ndim)


def union(arrays: typing.List[BufferObject]):

    if not len(arrays):
        return

    ndim = _get_common_num_dims(arrays)
    if ndim < 0:
        return

    if ndim == 1:
        tvec = []
        vdtype = np.int64
        for arr in arrays:
            try:
                tvec.extend(arr.tolist())
                if 'float' in str(arr.dtype):
                    vdtype = np.float64
            except AttributeError:
                continue
        return np.unique(np.array(tvec, dtype=vdtype)).view(BufferObject)
    else:
        raise InvalidNDims(ndim)
