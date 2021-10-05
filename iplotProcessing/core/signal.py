""" 
.. module:: signal
.. synopsis:: Coordinate and extend math capabilities to enable signal processing on multiple BufferObjects.
.. moduleauthor:: Jaswant Sai Panchumarti <jaswant.panchumarti@iter.org, jspanchu@gmail.com>
"""

from dataclasses import dataclass, field, fields
from operator import attrgetter
from scipy.interpolate import interp1d
import numpy as np
import typing

from iplotProcessing.common.errors import InvalidExpression
from iplotProcessing.common.interpolation import InterpolationKind
from iplotProcessing.common.time_mixing import TimeAlignmentMode
from iplotProcessing.common.units import DATE_TIME_PRECISE
from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.tools import parsers

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "DEBUG")

SignalT = typing.TypeVar("SignalT", bound="Signal")


@dataclass
class Signal:
    """A processing object meant to provide data, unit handling for multi-dimensional
    signal processing methods.

    :param data_source: name of the data source for this signal.
    :param name: name of this signal.
    :param expression: an expression for this signal.


    Create a signal

        >>> from iplotProcessing.core import Signal
        >>> s = Signal(name='VAR-123-XYZ', data_source='codacuda')
        >>> s.time
        BufferObject([], dtype=float64)
        >>> s.time_unit
        ''
        >>> s.data_primary
        BufferObject([], dtype=float64)
        >>> s.data_primary_unit
        ''
        >>> s.data_secondary
        BufferObject([], dtype=float64)
        >>> s.data_secondary_unit
        ''
        >>> s.rank
        0
        >>> s.is_expression
        False

    .. note::

       The data_store is made of of primary and secondary data objects.
       By default, simply use `data` member to get primary data object's buffer.


    """

    data_source: str = '' #: name of the data source for this signal.
    name: str = '' #: name of this signal.
    expression: str = '${self}' #: an expression for this signal.
    var_names: list = field(default_factory=list) #: a list of names of the constituent signals that make this signal. (read-only)

    def __post_init__(self) -> None:
        self._time = BufferObject()
        self._data_store = [BufferObject(), BufferObject()]
        self._mixing_mode = TimeAlignmentMode.INTERSECTION
        self._interp_kind = InterpolationKind.LINEAR

        self._other_bkp = [BufferObject(), BufferObject(), BufferObject()]
        self._self_bkp = [BufferObject(), BufferObject(), BufferObject()]

    def __operator_dispatch__(self, operator, other):
        """Ensure proper alignment of time bases prior to application of an operator.

        :param operator: a valid python operator. (unused)
        :type operator: type
        :param other: another signal
        :type other: Signal
        """
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

    def log_string(self) -> None:
        yield f"Signal instance: {id(self)}"

        for field in fields(self):
            yield f"self.{field.name}: {getattr(self, field.name)}"
        yield f"self.is_composite: {self.is_composite}"
        yield f"len(self.var_names): {len(self.var_names)}"
        yield f"self.is_expression: {self.is_expression}"

    @property
    def rank(self) -> int:
        """Compute the rank of this signal.

        rank = ndims(primary_data) + ndims(secondary_data)

        Example 
            g = f(t) -> rank = 1
            g = f(x, t) 
            -> rank = 3 if x is 1-D

        :return: rank
        :rtype: int
        """
        if self._data_store[0].size and self._data_store[1].size:
            return np.sum(list(map(attrgetter('ndim'), self._data_store)))
        elif self._data_store[0].size:
            return self._data_store[0].ndim
        elif self._data_store[1].size:
            return self._data_store[1].ndim
        else:
            return 0

    @property
    def is_composite(self) -> bool:
        """A signal is composite if it has two or more constituent signals.

        :return: True if composite else False
        :rtype: bool
        """
        return len(self.var_names) > 1

    @property
    def is_expression(self) -> bool:
        """Determine if the name of this signal is an expression.

        >>> print(Signal(name='${ml0004}').is_expression)
        True
        >>> print(Signal(name='CWS-SCSU-HR00:ML0004-LT-XI').is_expression)
        False
        >>> print(Signal(name='${CWS-SCSU-HR00:ML0004-LT-XI}').is_expression)
        True
        >>> print(Signal(name='${ml0004}-{ml0002}').is_expression)
        False
        >>> print(Signal(name='{ml0004}-{ml0002}').is_expression)
        False
        >>> print(Signal(name='${ml0004}-${ml0002}').is_expression)
        True

        :return: True if name is an expression else False
        :rtype: bool
        """
        try:
            return parsers.Parser().set_expression(self.name).is_valid
        except InvalidExpression:
            return False

    def set_expression(self, val: str):
        """Set the expression for this signal.

        .. note:: 
            if val is an empty string or a white-space string, the expression is set to '${self}'

        :param val: A valid expression string.
        :type val: str
        :raises InvalidExpression: when the expression is valid.
        """
        if (isinstance(val, property)):
            val = "${self}"
        if not isinstance(val, str):
            raise InvalidExpression
        if not len(val) or val.isspace():
            val = "${self}"
        self.expression = val

    @property
    def time(self) -> BufferObject:
        """The time buffer for this signal.

        :return: a buffer object.
        :rtype: BufferObject
        """
        return self._time

    @time.setter
    def time(self, val):
        if isinstance(val, BufferObject):
            self._time = val
        else:
            self._time = BufferObject(input_arr=val)
        self._time = self._time.ravel().view(BufferObject)  # time has to be a 1D array!

    @property
    def data_primary(self) -> BufferObject:
        """The primary data for this signal.

        :return: a buffer object.
        :rtype: BufferObject
        """
        return self._data_store[0]

    @data_primary.setter
    def data_primary(self, val):
        if isinstance(val, BufferObject):
            self._data_store[0] = val
        else:
            self._data_store[0] = BufferObject(input_arr=val)

    @property
    def data_secondary(self) -> BufferObject:
        """The secondary data for this signal.

        :return: a buffer object.
        :rtype: BufferObject
        """
        return self._data_store[1]

    @data_secondary.setter
    def data_secondary(self, val):
        if isinstance(val, BufferObject):
            self._data_store[1] = val
        else:
            self._data_store[1] = BufferObject(input_arr=val)

    @property
    def time_unit(self) -> str:
        """The time unit for this signal.

        :return: a string (ex: 'ns', 's', 'D', 'ms') See :mod:`iplotProcessing.common.units`
        :rtype: str
        """
        return self._time.unit

    @time_unit.setter
    def time_unit(self, val):
        self._time.unit = val

    @property
    def data_unit(self) -> str:
        """The primary data unit for this signal.

        :return: a string (ex: 'C', 'kV', 'J', 'A')
        :rtype: str
        """
        return self._data_store[0].unit

    @data_unit.setter
    def data_unit(self, val):
        self._data_store[0].unit = val

    @property
    def data_primary_unit(self) -> str:
        """The primary data unit for this signal.

        :return: a string (ex: 'C', 'kV', 'J', 'A')
        :rtype: str
        """
        return self._data_store[0].unit

    @data_primary_unit.setter
    def data_primary_unit(self, val):
        self._data_store[0].unit = val

    @property
    def data_secondary_unit(self) -> str:
        """The secondary data unit for this signal.

        :return: a string (ex: 'C', 'kV', 'J', 'A')
        :rtype: str
        """
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
                dp_unit = sig.data_primary_unit
                sig.data_primary = BufferObject(
                    input_arr=f_primary(sig.time), unit=dp_unit)
            if f_secondary:
                ds_unit = sig.data_secondary_unit
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


def __union__(signals: typing.List[Signal], kind=InterpolationKind.LINEAR):

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
