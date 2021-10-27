# Description: Coordinate and extend math capabilities to enable signal processing on multiple BufferObjects.
# Author: Jaswant Sai Panchumarti

from scipy.interpolate import interp1d
import numpy as np
import typing

from iplotProcessing.common.interpolation import InterpolationKind
from iplotProcessing.common.time_mixing import TimeAlignmentMode
from iplotProcessing.common.units import DATE_TIME_PRECISE
from iplotProcessing.core.bobject import BufferObject

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "INFO")

SignalT = typing.TypeVar("SignalT", bound="Signal")

class Signal:
    """Provides data, unit handling for multi-dimensional signal processing methods.

    The data_store is made of of primary and secondary data objects.
    By default, simply use `data` member to get primary data object's buffer

    Note on signal math
    ===================
    When a signal is combined with other signals in mathematical expression,
    the default mixing mode for time alignment is an intersection
    of the individual time arrays.

    The data values are then interpolated onto this new common time base.
    The default kind of interpolation is linear.

    Time
    ====
    This is the time base for a signal, it could as well be another signal's data buffers.

    Primary data
    ============
    This is the data that is dependent on time. (could be independent)

    Secondary data
    ============
    This is the data that is dependent on time. (could be independent)

    Examples
    ============
    1. For 1D signals:
        Ip = f(t)

        data_primary would be 'Ip'
        time would correspond to 't' variable

    2. For 2D signals:
        Te = f(t, r)

        data_primary could be 'Te'
        data_secondary could be 'r'
        time would correspond to 't' variable.

        Note:

            time's buffer could as well be replaced by data_primary from the first example.
            i.e, Te = f(Ip, r)

    The name 'time' simply implies that it could be the basis for the data buffers.
    It also helps in simpler naming of singal processing methods.

    """

    def __init__(self):
        self._time = BufferObject()
        self._data_store = [BufferObject(), BufferObject()]
        self._mixing_mode = TimeAlignmentMode.INTERSECTION
        self._interp_kind = InterpolationKind.LINEAR

        self._other_bkp = [BufferObject(), BufferObject(), BufferObject()]
        self._self_bkp = [BufferObject(), BufferObject(), BufferObject()]

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        # Apply to data_store.
        result_signals = [type(self)()] * ufunc.nout

        for idx, buffer in enumerate(self._data_store):
            args = ((i._data_store[idx] if isinstance(i, Signal) else i)
                    for i in inputs)
            outputs = kwargs.pop('out', None)
            if outputs:
                kwargs['out'] = tuple((o._data_store[idx] if isinstance(
                    o, Signal) else o) for o in outputs)
            else:
                outputs = (None,) * ufunc.nout
            try:
                results = buffer.__array_ufunc__(ufunc, method, *args,
                                                 **kwargs)  # pylint: disable=no-member
            except Exception as e:
                logger.debug(e)
                continue

            if results is NotImplemented:
                return NotImplemented
            if method == 'at':
                return
            if ufunc.nout == 1:
                results = (results,)

            results = tuple((result if output is None else output)
                            for result, output in zip(results, outputs))

            iout = 0
            for ds, output in zip(results, outputs):
                if output is None:
                    result_signals[iout].time = self.time # implicit
                    if np.isscalar(ds):
                        ds = BufferObject([ds] * len(self._time), self._data_store[idx].unit)
                    elif len(ds) == 1:
                        ds = BufferObject([ds[0]] * len(self._time), self._data_store[idx].unit)
                    result_signals[iout]._data_store[idx] = ds
                else:
                    if np.isscalar(ds):
                        ds = BufferObject([ds] * len(output._time), output._data_store[idx].unit)
                    elif len(ds) == 1:
                        ds = BufferObject([ds[0]] * len(output._time), output._data_store[idx].unit)
                    output._data_store[idx] = ds
                    result_signals[iout] = output
                iout += 1

        return result_signals[0] if len(result_signals) == 1 else result_signals

    def __operator_dispatch__(self, operator, other):
        self._self_bkp = [self.time, self.data_primary, self.data_secondary]
        if isinstance(other, Signal):
            self._other_bkp = [other.time,
                               other.data_primary, other.data_secondary]
            __align__([self, other], self._mixing_mode, self._interp_kind)

    def __post_operator__(self, operator, other):
        self.time = self._self_bkp[0]
        self._data_store = [self._self_bkp[1], self._self_bkp[2]]
        if isinstance(other, Signal):
            other.time = self._other_bkp[0]
            other._data_store = [self._other_bkp[1], self._other_bkp[2]]

    def __add__(self, other):
        self.__operator_dispatch__(self.__add__, other)
        sig = type(self)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] + other
            else:
                sig._data_store[i] = self._data_store[i] + other._data_store[i]
        self.__post_operator__(self.__add__, other)
        return sig

    def __sub__(self, other):
        self.__operator_dispatch__(self.__sub__, other)
        sig = type(self)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] - other
            else:
                sig._data_store[i] = self._data_store[i] - other._data_store[i]
        self.__post_operator__(self.__sub__, other)
        return sig

    def __mul__(self, other):
        self.__operator_dispatch__(self.__mul__, other)
        sig = type(self)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] * other
            else:
                sig._data_store[i] = self._data_store[i] * other._data_store[i]
        self.__post_operator__(self.__mul__, other)
        return sig

    def __truediv__(self, other):
        self.__operator_dispatch__(self.__truediv__, other)
        sig = type(self)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] / other
            else:
                sig._data_store[i] = self._data_store[i] / other._data_store[i]
        self.__post_operator__(self.__truediv__, other)
        return sig

    def __floordiv__(self, other):
        self.__operator_dispatch__(self.__floordiv__, other)
        sig = type(self)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] // other
            else:
                sig._data_store[i] = self._data_store[i] // other._data_store[i]
        self.__post_operator__(self.__floordiv__, other)
        return sig

    def copy_buffers_to(self, other: SignalT):
        other._time = self._time
        other._data_store[0] = self._data_store[0]
        other._data_store[1] = self._data_store[1]

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val):
        if isinstance(val, BufferObject):
            self._time = val
        else:
            self._time = BufferObject(input_arr=val)
        self._time = self._time.ravel().view(BufferObject)  # time has to be a 1D array!

    @property
    def data(self):
        return self.data_primary

    @data.setter
    def data(self, val):
        self.data_primary = val

    @property
    def data_primary(self):
        return self._data_store[0]

    @data_primary.setter
    def data_primary(self, val):
        if isinstance(val, BufferObject):
            self._data_store[0] = val
        else:
            self._data_store[0] = BufferObject(input_arr=val)

    @property
    def data_secondary(self):
        return self._data_store[1]

    @data_secondary.setter
    def data_secondary(self, val):
        if isinstance(val, BufferObject):
            self._data_store[1] = val
        else:
            self._data_store[1] = BufferObject(input_arr=val)

    @property
    def time_unit(self):
        return self._time.unit

    @time_unit.setter
    def time_unit(self, val):
        self._time.unit = val

    @property
    def data_unit(self):
        return self._data_store[0].unit

    @data_unit.setter
    def data_unit(self, val):
        self._data_store[0].unit = val

    @property
    def data_primary_unit(self):
        return self._data_store[0].unit

    @data_primary_unit.setter
    def data_primary_unit(self, val):
        self._data_store[0].unit = val

    @property
    def data_secondary_unit(self):
        return self._data_store[1].unit

    @data_secondary_unit.setter
    def data_secondary_unit(self, val):
        self._data_store[1].unit = val


def __align__(signals: typing.List[Signal], mode=TimeAlignmentMode.INTERSECTION, kind=InterpolationKind.LINEAR):
    if mode == TimeAlignmentMode.INTERSECTION:
        common_time = __intersection__(signals, kind)
    elif mode == TimeAlignmentMode.UNION:
        common_time = __union__(signals, kind)
    else:
        logger.warning(f"Unsupported alignment mode: {mode}")
        return

    time_unit = __get_finest_time_unit__(signals)

    # rebase every signal to a common time buffer object
    for sig in signals:
        try:
            # interpolate from old time vector
            if len(sig.data_primary) and sig.data_primary.ndim == 1:
                f_primary = interp1d(
                    sig.time, sig.data_primary, kind=kind, fill_value='extrapolate')
            else:
                f_primary = None
            if len(sig.data_secondary) and sig.data_secondary.ndim == 1:
                f_secondary = interp1d(
                    sig.time, sig.data_secondary, kind=kind, fill_value='extrapolate')
            else:
                f_secondary = None

            sig.time = BufferObject(input_arr=common_time, unit=time_unit)
            if f_primary:
                dp_unit = sig.data_primary.unit
                sig.data_primary = BufferObject(
                    input_arr=f_primary(sig.time), unit=dp_unit)
            if f_secondary:
                ds_unit = sig.data_secondary.unit
                sig.data_secondary = BufferObject(
                    input_arr=f_secondary(sig.time), unit=ds_unit)
        except AttributeError:
            continue


def __get_finest_time_unit__(signals: typing.List[Signal]) -> str:
    idx = -1
    for sig in signals:
        try:
            idx = max(DATE_TIME_PRECISE.index(sig.time_unit), idx)
        except (ValueError, AttributeError) as _:
            continue

    return DATE_TIME_PRECISE[idx]


def __get_coarsest_time_unit__(signals: typing.List[Signal]) -> str:
    idx = len(DATE_TIME_PRECISE) - 1
    for sig in signals:
        try:
            idx = min(DATE_TIME_PRECISE.index(sig.time_unit), idx)
        except (ValueError, AttributeError) as _:
            continue

    return DATE_TIME_PRECISE[idx]


def __intersection__(signals: typing.List[Signal], kind=InterpolationKind.LINEAR):

    num_points = 0
    tmin = np.iinfo(np.int64).min
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


def __union__(signals: typing.List[Signal], kind=InterpolationKind.LINEAR):

    time_dtype = np.int64
    tvec = []
    for sig in signals:
        try:
            tvec.extend(sig.time.tolist())
            if 'float' in str(sig.time.dtype):
                time_dtype = np.float64
        except AttributeError:
            continue
    tvec = np.unique((np.array(tvec, dtype=time_dtype)))
    return tvec
