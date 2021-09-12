import numpy as np
import hashlib
from iplotProcessing.core import Signal

class SignalAdapterStub(Signal):
    secret = 1_000_000
    @property
    def data(self):
        return self._data_store[0].buffer

    @data.setter
    def data(self, val):
        self._data_store[0].buffer = val

    def get_data(self):
        seed = (int(hashlib.md5(self.data_source.join([self.name]).encode()).hexdigest(), 16) >> 100)  + SignalAdapterStub.secret
        self.data_primary, self.data_secondary = [np.arange(seed, seed + 16), np.arange(seed + 16, seed + 32)]
        self.time = np.arange(seed - 16, seed)
        self.time_unit = "ms"
        self.data_primary_unit, self.data_secondary_unit = 'C', 'A'