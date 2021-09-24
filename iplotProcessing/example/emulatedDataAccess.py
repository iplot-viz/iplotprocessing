# Description: Example blueprints of stubs necessary to use the iplotProcessing infrastructure
# Author: Jaswant Sai Panchumarti

from collections import namedtuple
from dataclasses import dataclass

import numpy as np
import hashlib
from iplotProcessing.core import BufferObject, Context, Signal
from iplotProcessing.tools import hash_code

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="DEBUG")

DataObjStub = namedtuple("DataObjStub", [
                         "xdata", "ydata", "zdata", "xunit", "yunit", "zunit"], defaults=[None, None, None, '', '', ''])


class DataAccessStub:
    def getData(self, data_source, var_name):
        logger.info(f"Fetching data: DS={data_source}, var_name={var_name}")
        seed_str = data_source.join([var_name])
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) >> 100
        seed += SignalAdapterStub.secret
        return DataObjStub(np.arange(seed - 16, seed), np.arange(seed, seed + 16), np.arange(seed + 16, seed + 32), 'ms', 'C', 'A')


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
    plot_type: str = ''

    def __post_init__(self):
        Signal.__post_init__(self)

        if self.ts_start is not None:
            self.ts_start = np.datetime64(self.ts_start, 'ns').astype(
                'int64').item() if isinstance(self.ts_start, str) else self.ts_start

        if self.ts_end is not None:
            self.ts_end = np.datetime64(self.ts_end, 'ns').astype(
                'int64').item() if isinstance(self.ts_end, str) else self.ts_end

        if self.title is None:
            self.title = self.name or ''

        if self.pulse_nb is not None:
            self.ts_relative = True
            self.title += ':' + str(self.pulse_nb)

        self.param_hash = ''

    @property
    def data(self):
        return self._data_store[0]

    @data.setter
    def data(self, val):
        self._data_store[0] = BufferObject(input_arr=val)

    def fetch_data(self):
        if self.needs_refresh():
            AccessHelperStub.get().fetch_data(self)

    def get_data(self):
        self_hash = hash_code(self, ["data_source", "name"])
        x_data = AccessHelperStub.get().ctx.evaluate_expr(
            self.x_expr, self_hash, data_source=self.data_source)
        y_data = AccessHelperStub.get().ctx.evaluate_expr(
            self.y_expr, self_hash, data_source=self.data_source)
        z_data = AccessHelperStub.get().ctx.evaluate_expr(
            self.z_expr, self_hash, data_source=self.data_source)

        if len(x_data) > 1:
            self.data_xrange = self.time[0], self.time[-1]

        print(x_data)
        print(y_data)
        print(z_data)

        return [x_data, y_data, z_data]

    def needs_refresh(self) -> bool:
        cur_hash = hash_code(
            self, ["ts_start", "ts_end", "dec_samples", "pulse_nb"])
        if self.param_hash != cur_hash:
            self.param_hash = cur_hash
            if self.dec_samples == -1:  # and self._check_if_zoomed_in():
                return False
            else:
                return True
        return False


class AccessHelperStub:
    da: DataAccessStub = None
    ctx: Context = None

    @staticmethod
    def get():
        return AccessHelperStub()

    def fetch_data(self, signal: SignalAdapterStub):
        if not isinstance(signal, SignalAdapterStub):
            logger.warning(
                f"{signal} is not an object of {type(SignalAdapterStub)}")
            return

        # Evaluate self
        if signal.is_expression:
            self.ctx.evaluate_signal(
                signal, lambda h, sig: print(h, sig), get_as_needed=True)
        else:
            dobj = self.da.getData(signal.data_source, signal.name)
            signal.time = dobj.xdata
            signal.data_primary = dobj.ydata
            signal.data_secondary = dobj.zdata

            signal.time_unit = dobj.xunit
            signal.data_primary_unit = dobj.yunit
            signal.data_secondary_unit = dobj.zunit
