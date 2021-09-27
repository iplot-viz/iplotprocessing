import typing
import numpy as np
from scipy.interpolate import interp1d

from iplotProcessing.core import BufferObject, Signal
from iplotProcessing.common import DATE_TIME_PRECISE
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="INFO")


class TimeAlignmentModes:
    MINMAX = "minmax"
    UNION = "union"


class InterpolationKind:
    LINEAR = 'linear'
    NEAREST = 'nearest',
    NEAREST_UP = 'nearest-up',
    ZERO = 'zero',
    SLINEAR = 'slinear',
    QUADRATIC = 'quadratic',
    CUBIC = 'cubic',
    PREVIOUS = 'previous',
    NEXT = 'next',


def align(signals: typing.List[Signal], mode=TimeAlignmentModes.MINMAX, kind=InterpolationKind.LINEAR):
    if mode == TimeAlignmentModes.MINMAX:
        common_time = _min_max_align(signals, kind)
    elif mode == TimeAlignmentModes.UNION:
        common_time = _union_align(signals, kind)
    else:
        logger.warning(f"Unsupported alignment mode: {mode}")
        return
    
    time_unit = get_finest_time_unit(signals)
    # rebase every signal to a common time buffer object
    for sig in signals:
        try:
            # interpolate from old time vector
            if len(sig.data_secondary) and sig.data_secondary.ndim == 1:
                f_primary = interp1d(sig.time, sig.data_primary, kind=kind)
            else:
                f_primary = None
            if len(sig.data_secondary) and sig.data_secondary.ndim == 1:
                f_secondary = interp1d(sig.time, sig.data_secondary, kind=kind)
            else:
                f_secondary = None
            
            sig.time = BufferObject(input_arr=common_time, unit=time_unit)
            if f_primary:
                dp_unit = sig.data_primary_unit
                sig.data_primary = BufferObject(input_arr=f_primary(sig.time), unit=dp_unit)
            if f_secondary:
                ds_unit = sig.data_secondary_unit
                sig.data_secondary = BufferObject(input_arr=f_secondary(sig.time), unit=ds_unit)
        except AttributeError:
            continue


def get_finest_time_unit(signals: typing.List[Signal]) -> str:
    idx = -1
    for sig in signals:
        try:
            idx = max(DATE_TIME_PRECISE.index(sig.time_unit), idx)
        except (ValueError, AttributeError) as _:
            continue

    return DATE_TIME_PRECISE[idx]


def get_coarsest_time_unit(signals: typing.List[Signal]) -> str:
    idx = len(DATE_TIME_PRECISE) - 1
    for sig in signals:
        try:
            idx = min(DATE_TIME_PRECISE.index(sig.time_unit), idx)
        except (ValueError, AttributeError) as _:
            continue

    return DATE_TIME_PRECISE[idx]


def _min_max_align(signals: typing.List[Signal], kind=InterpolationKind.LINEAR):

    num_points = 0
    tmin = 0
    tmax = np.iinfo(np.int64).max
    time_dtype = np.int64
    
    for sig in signals:
        try:
            tmin = max(min(sig.time), tmin)
            tmax = min(max(sig.time), tmax)
            num_points = max(sig.time.size, num_points)
            if 'float' in str(sig.time.dtype):
                time_dtype = np.float64
        except AttributeError:
            continue
    
    tvec = np.linspace(tmin, tmax, num_points + 1, dtype=time_dtype)
    return tvec


def _union_align(signals: typing.List[Signal], kind=InterpolationKind.LINEAR):
    
    num_points = 0
    tmin = np.iinfo(np.int64).max
    tmax = 0
    time_dtype = np.int64

    for sig in signals:
        try:
            tmin = min(min(sig.time), tmin)
            tmax = max(max(sig.time), tmax)
            num_points += sig.time.size
            if 'float' in str(sig.time.dtype):
                time_dtype = np.float64
        except AttributeError:
            continue
    
    tvec = np.linspace(tmin, tmax, num_points, dtype=time_dtype)
    return tvec

