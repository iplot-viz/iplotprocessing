from dataclasses import dataclass
import numpy as np
import hashlib
from iplotProcessing.core.bobject import BufferObject
from iplotProcessing.core import Signal

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="DEBUG")

@dataclass
class SignalAdapterStub(Signal):
    secret = 1_000_000
    title: str = None
    pulse_nb: int = None
    ts_start: int = None
    ts_end: int = None
    dec_samples: int = None
    ts_relative: bool = False
    envelope: bool = False
    x_expr: str = ''
    y_expr: str = ''
    z_expr: str = ''
    
    def __post_init__(self):
        Signal.__post_init__(self)
    
        if self.ts_start is not None:
            self.ts_start = np.datetime64(self.ts_start, 'ns').astype('int64').item() if isinstance(self.ts_start, str) else self.ts_start

        if self.ts_end is not None:
            self.ts_end = np.datetime64(self.ts_end, 'ns').astype('int64').item() if isinstance(self.ts_end, str) else self.ts_end

        if self.title is None:
            self.title = self.name or ''

        if self.pulse_nb is not None:
            self.title += ':' + str(self.pulse_nb)

        # Account for pulse_nb in name. 
        self.name = self.title

    @property
    def data(self):
        return self._data_store[0]

    @data.setter
    def data(self, val):
        self._data_store[0] = BufferObject(input_arr=val)

    def get_data(self):
        logger.info(f"Fetching data: DS={self.data_source}, var_name={self.name}")
        seed = (int(hashlib.md5(self.data_source.join([self.name]).encode()).hexdigest(), 16) >> 100)  + SignalAdapterStub.secret
        self.data_primary, self.data_secondary = [np.arange(seed, seed + 16), np.arange(seed + 16, seed + 32)]
        self.time = np.arange(seed - 16, seed)
        self.time_unit = "ms"
        self.data_primary_unit, self.data_secondary_unit = 'C', 'A'