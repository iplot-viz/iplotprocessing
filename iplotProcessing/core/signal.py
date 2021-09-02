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


    @property
    def time(self):
        return self._time.buffer

    @time.setter
    def time(self, val):
        self._time.buffer = val
        self._time.buffer = self._time.buffer.ravel() # time has to be a 1D array!

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
