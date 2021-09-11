from iplotProcessing.common.errors import InvalidExpression, InvalidSignalName
from iplotProcessing.core.dobject import DObject
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "DEBUG")


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

    def __init__(self) -> None:

        self._time = DObject()
        self._data_store = [DObject(), DObject()]

        self._data_source = ""
        self._name = ""
        self._expression = ""
        self._var_names = set()

    def __add__(self, other):
        sig = Signal()
        sig._time = self._time + other._time
        for i in range(2):
            sig._data_store[i] = self._data_store[i] + other._data_store[i]
        return sig

    def __sub__(self, other):
        sig = Signal()
        sig._time = self._time - other._time
        for i in range(2):
            sig._data_store[i] = self._data_store[i] - other._data_store[i]
        return sig

    def debug_log(self) -> str:
        logger.debug(f"Signal instance: {id(self)}")
        logger.debug(f"self.name: {self.name}")
        logger.debug(f"self.expression: {self.expression}")
        logger.debug(f"self.data_source: {self.data_source}")
        logger.debug(f"self.composite: {self.is_composite()}")
        logger.debug(f"len(self.var_names): {len(self.var_names)}")

    def is_composite(self) -> bool:
        return len(self._var_names) > 1

    @property
    def data_source(self):
        return self._data_source

    @data_source.setter
    def data_source(self, val: str):
        self._data_source = val

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, val: str):
        if not isinstance(val, str):
            raise InvalidExpression
        elif not len(val):
            raise InvalidExpression
        self._expression = val

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val: str):
        if not isinstance(val, str):
            raise InvalidSignalName
        elif not len(val):
            raise InvalidSignalName
        self._name = val

    @property
    def var_names(self):
        return self._var_names

    @property
    def time(self):
        return self._time.buffer

    @time.setter
    def time(self, val):
        self._time.buffer = val
        self._time.buffer = self._time.buffer.ravel()  # time has to be a 1D array!

    @property
    def data(self):
        return self._data_store[0].buffer

    @data.setter
    def data(self, val):
        self._data_store[0].buffer = val

    @property
    def data_primary(self):
        return self._data_store[0].buffer

    @data_primary.setter
    def data_primary(self, val):
        self._data_store[0].buffer = val

    @property
    def data_secondary(self):
        return self._data_store[1].buffer

    @data_secondary.setter
    def data_secondary(self, val):
        self._data_store[1].buffer = val

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
