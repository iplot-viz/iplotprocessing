from collections import defaultdict
from typing import Dict, Union
from iplotProcessing.core.processor import Processor
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher, parsers


class Context:
    def __init__(self) -> None:
        self._processors = defaultdict(list)
        self._env = {}         # type: Dict[str, Union[Signal, str]]

    def getReference(self, sourceId: str, name: str) -> Union[Signal, str]:
        key = hasher.hash_tuple((sourceId, name))
        return self._env.get(key)

    def getProcessor(self, sourceId: str, inputExpr: str) -> Processor:
        key = hasher.hash_tuple((sourceId, inputExpr))
        return self._processors.get(key)

    def updateAlias(self, sourceId: str, name: str, alias: str):
        key = hasher.hash_tuple((sourceId, name))
        self._env.update({alias: key})

    def register(self, proc: Processor):
        if proc is None:
            return

        key = hasher.hash_tuple((proc.sourceId, proc.inputExpr))
        self.processors.update({key: proc})
        proc.gEnv = self.env

    def deRegister(self, proc: Processor):
        if proc is None:
            return

        key = hasher.hash_tuple((proc.sourceId, proc.inputExpr))
        self.processors.pop(key)
        proc.gEnv = None

    def refresh(self):
        for proc in self.processors.values():
            parser = parsers.ExprParser()
            parser.setExpr(proc.inputExpr)

            keys = parser.vardict.keys()
            if not parser.isExpr:  # for single varname without '${', '}'
                keys = [proc.inputExpr]

            # create a signal instance for each variable that isn't an alias
            for varName in keys:
                key = hasher.hash_tuple((proc.sourceId, varName))
                if self._env.get(varName) is None:  # ensure varName is not aliased
                    self._env.update({key: Signal()})

    @property
    def processors(self):
        return self._processors

    @processors.setter
    def processors(self, val):
        raise AttributeError("Restricted access. Cannot assign processors.")

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, val: dict):
        raise AttributeError(
            "Restricted access. Cannot assign non dictionary object to environment.")
