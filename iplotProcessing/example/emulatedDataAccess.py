import numpy as np
import hashlib
from iplotProcessing.translators.datasources.emulated import DObj

class DataAccess:
    secret = 1_000_000
    @staticmethod
    def getData(source: str="b", varname: str="a", tsS=0, tsE=1):
        seed = (int(hashlib.md5(source.join([varname]).encode()).hexdigest(), 16) >> 100)  + DataAccess.secret
        dataInst = DObj()
        dataInst.data = [np.arange(seed, seed + 16), np.arange(seed + 16, seed + 32)]
        dataInst.time = [np.arange(seed - 16, seed)]
        dataInst.time_unit = "ms"
        dataInst.data_units = ['C', 'A']
        return dataInst