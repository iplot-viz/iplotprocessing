# Description: Coordinate and extend math capabilities to enable signal processing on multiple BufferObjects.
# Author: Jaswant Sai Panchumarti

import numpy as np
import typing

from iplotProcessing.core.bobject import BufferObject

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "INFO")

SignalT = typing.TypeVar("SignalT", bound="Signal")


class Signal:
    """Provides data, unit handling for multi-dimensional signal processing methods.
    Multi-dimensional buffer objects are stored in an internal list.
    The alias map is a dictionary that maps indices of the internal list to a human-readable accessor.

    The default alias map = {
            'time': {'idx': 0, 'independent': True},
            'data': {'idx': 1},
        }
    So, signal.time -> signal.data_store[0]
        signal.data -> signal.data_store[1]

    Example 1:

        signal.alias_map = {
                        'r': {'idx': 0, 'independent': True},
                        'z': {'idx': 1, 'independent': True},
                        'psi': {'idx': 2}
                    }
        then,
        signal.r -> signal.data_store[0]
        signal.z -> signal.data_store[1]
        signal.psi -> signal.data_store[2]

    Example 2:

        signal.alias_map = {
                        'time': {'idx': 0, 'independent': True},
                        'dmin': {'idx': 1},
                        'dmax': {'idx': 2}
                    }
        then,
        signal.time -> signal.data_store[0]
        signal.dmin -> signal.data_store[1]
        signal.dmax -> signal.data_store[2]

    Warning:
        You can only use the keys of the alias map to 'get' the values. You should not use those for setting the data.
        The list of underlying data is exposed as the 'data_store' property.
        Use the data_store list to set the underlying data.
    """

    def __init__(self):
        self._data = [BufferObject(), BufferObject(), BufferObject()]
        self._alias_map = {
            'time': {'idx': 0, 'independent': True},
            'data': {'idx': 1},
        }

    @property
    def alias_map(self):
        return self._alias_map

    @property
    def data_store(self):
        return self._data

    @property
    def dependent_accessors(self):
        accessors = []
        for v in self._alias_map.values():
            idx = v.get('idx')
            if not v.get('independent'):
                accessors.append(idx)
        return accessors

    @property
    def independent_accessors(self):
        accessors = []
        for v in self._alias_map.values():
            idx = v.get('idx')
            if v.get('independent'):
                accessors.append(idx)
        return accessors

    @property
    def rank(self):
        rank = 0
        for i in self.dependent_accessors:
            rank += self._data[i].ndim
        return rank

    def __add__(self, other):
        return np.add(self, other)

    def __sub__(self, other):
        return np.subtract(self, other)

    def __mul__(self, other):
        return np.multiply(self, other)

    def __neg__(self):
        return self.__mul__(-1)

    def __multiply__(self, other):
        return np.multiply(self, other)

    def __truediv__(self, other):
        return np.true_divide(self, other)

    def __floordiv__(self, other):
        return np.floor_divide(self, other)

    def __getattr__(self, name: str):
        if name not in self.__dict__['_alias_map']:
            try:
                return self.__dict__[name]
            except KeyError:
                raise AttributeError(name)
        else:
            idx = self.__dict__['_alias_map'][name].get('idx')
            return self._data[idx]

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        result_signals = [type(self)()] * ufunc.nout
        indep_accessors = self.independent_accessors
        for sig in result_signals:
            sig._alias_map = dict(self._alias_map)
            sig._data.clear()
            for i in range(len(self._data)):
                if i in indep_accessors:
                    sig._data.append(self._data[i])
                else:
                    sig._data.append(BufferObject())

        for idx in self.dependent_accessors:
            args = ((i._data[idx] if isinstance(i, Signal) else i)
                    for i in inputs)
            outputs = kwargs.pop('out', None)
            if outputs:
                kwargs['out'] = tuple((o._data[idx] if isinstance(
                    o, Signal) else o) for o in outputs)
            else:
                outputs = (None,) * ufunc.nout

            results = self._data[idx].__array_ufunc__(ufunc, method, *args,
                                                        **kwargs)  # pylint: disable=no-member

            if results is NotImplemented:
                return NotImplemented
            if method == 'at':
                return
            if ufunc.nout == 1:
                results = (results,)

            results = tuple((result if output is None else output)
                            for result, output in zip(results, outputs))

            iout = 0
            for result, output in zip(results, outputs):
                if output is None:
                    result_signals[iout]._data[idx] = result
                else:
                    output._data[idx] = result
                    result_signals[iout] = output
                iout += 1

        return result_signals[0] if len(result_signals) == 1 else result_signals
