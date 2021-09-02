import typing
from iplotProcessing.common.parameter_id import getParamsId
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher

class UnboundSignalError(Exception):
    def __init__(self, hc: str):
        self.hashCode = hc

class Environment(dict):
    def isAlias(self, name: str):
        return isinstance(self.get(name), str)

    def getSignal(self, dataSource: str, name: str, **kwargs) -> typing.Tuple[str, Signal]:
        paramsId = getParamsId(kwargs)
        hashCode = hasher.hash_tuple((dataSource, name, paramsId))
        value = self.get(hashCode)

        if not isinstance(value, Signal):
            value = name
            while self.isAlias(value):
                value = self.get(name)
                hashCode = value
        
        value = self.get(hashCode)
        if not isinstance(value, Signal):
            raise UnboundSignalError(hashCode)
    
        return hashCode, value

    def updateAlias(self, dataSource: str, name: str, alias: str, **kwargs):
        paramsId = getParamsId(kwargs)
        key = hasher.hash_tuple((dataSource, name, paramsId))
        self.update({alias: key})
