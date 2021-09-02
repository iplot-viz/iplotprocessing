import numpy as np


class DObject:
    """A data object with a flat 1-d buffer to hold the data values
       and a unit attribute corresponding to the values
    """

    def __init__(self) -> None:
        self.unit: str = ""
        self._buffer: np.ndarray = np.array([])

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, val):
        self._buffer = np.asarray(val)

    def __add__(self, other):
        dobj = DObject()
        dobj.buffer = self.buffer + other.buffer
        dobj.unit = self.unit
        return dobj

    def __sub__(self, other):
        dobj = DObject()
        dobj.buffer = self.buffer - other.buffer
        dobj.unit = self.unit
        return dobj

    def __getattr__(self, attr):
        """Makes the object behave like a numpy.ndarray"""
        if hasattr(self._buffer, attr):
            return getattr(self._buffer, attr)
        else:
            raise AttributeError(self.__class__.__name__ +
                  " has no attribute named " + attr)
