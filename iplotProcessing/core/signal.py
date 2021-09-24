# Description: Coordinate and extend math capabilities to enable signal processing on multiple BufferObjects.
# Author: Jaswant Sai Panchumarti

from dataclasses import dataclass, field
import numpy as np
import typing

from iplotProcessing.common.errors import InvalidExpression
from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.tools import parsers

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "DEBUG")

SignalT = typing.TypeVar("SignalT", bound="Signal")

@dataclass
class Signal:
    """A processing object meant to provide data, unit handling for multi-dimensional
    signal processing methods.

    The data_store is made of of primary and secondary data objects.
    By default, simply use `data` member to get primary data object's buffer

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
    data_source: str=""
    name: str=""
    expression: str = ""
    var_names: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self._time = BufferObject()
        self._data_store = [BufferObject(), BufferObject()]

    def __add__(self, other):
        sig = type(other)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] + other
            else:
                sig._data_store[i] = self._data_store[i] + other._data_store[i]
        return sig

    def __sub__(self, other):
        sig = type(other)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] - other
            else:
                sig._data_store[i] = self._data_store[i] - other._data_store[i]
        return sig

    def __mul__(self, other):
        sig = type(other)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] * other
            else:
                sig._data_store[i] = self._data_store[i] * other._data_store[i]
        return sig

    def __truediv__(self, other):
        sig = type(other)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] / other
            else:
                sig._data_store[i] = self._data_store[i] / other._data_store[i]
        return sig

    def __floordiv__(self, other):
        sig = type(other)()
        sig._time = self._time
        for i in range(2):
            if np.isscalar(other) or isinstance(other, np.ndarray):
                sig._data_store[i] = self._data_store[i] // other
            else:
                sig._data_store[i] = self._data_store[i] // other._data_store[i]
        return sig

    def copy_buffers_to(self, other: SignalT):
        other._time = self._time
        other._data_store[0] = self._data_store[0]
        other._data_store[1] = self._data_store[1]

    def debug_log(self) -> str:
        logger.debug(f"Signal instance: {id(self)}")
        logger.debug(f"self.name: {self.name}")
        logger.debug(f"self.expression: {self.expression}")
        logger.debug(f"self.data_source: {self.data_source}")
        logger.debug(f"self.composite: {self.is_composite}")
        logger.debug(f"len(self.var_names): {len(self.var_names)}")
   
    @property
    def is_composite(self) -> bool:
        return len(self.var_names) > 1

    @property
    def is_expression(self) -> bool:
        return parsers.Parser().set_expression(self.name).is_valid

    def set_expression(self, val: str):
        if (isinstance(val, property)):
            val = "${self}"
        if not isinstance(val, str):
            raise InvalidExpression
        elif not len(val):
            val = "${self}"
        self.expression = val

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, val):
        self._time = BufferObject(input_arr=val)
        self._time = self._time.ravel().view(BufferObject)  # time has to be a 1D array!

    @property
    def data_primary(self):
        return self._data_store[0]

    @data_primary.setter
    def data_primary(self, val):
        self._data_store[0] = BufferObject(input_arr=val)

    @property
    def data_secondary(self):
        return self._data_store[1]

    @data_secondary.setter
    def data_secondary(self, val):
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
