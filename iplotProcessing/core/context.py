from collections import defaultdict
from typing import Any, Dict, Union
from iplotProcessing.core.processor import Processor
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher
from iplotProcessing.translators.translator import Translator


class Context:
    def __init__(self) -> None:
        self._processors = defaultdict(list)
        self._env = {}         # type: Dict[str, Union[Signal, str]]

    def getSignal(self, dataSource: str, name: str, **kwargs) -> Signal:
        paramsId = Processor.getParamsId(kwargs)
        key = hasher.hash_tuple((dataSource, name, paramsId))
        return self._env.get(key)

    def getProcessor(self, dataSource: str, inputExpr: str, **kwargs) -> Processor:
        paramsId = Processor.getParamsId(kwargs)
        key = hasher.hash_tuple((dataSource, inputExpr, paramsId))
        return self._processors.get(key)

    def updateAlias(self, dataSource: str, name: str, alias: str, **kwargs):
        paramsId = Processor.getParamsId(kwargs)
        key = hasher.hash_tuple((dataSource, name, paramsId))
        self._env.update({alias: key})

    def register(self, proc: Processor):
        if proc is None:
            return

        key = hasher.hash_code(proc, ["dataSource", "inputExpr", "paramsId"])
        self.processors.update({key: proc})
        proc.gEnv = self.env

    def deRegister(self, proc: Processor):
        if proc is None:
            return

        key = hasher.hash_code(proc, ["dataSource", "inputExpr", "paramsId"])
        self.processors.pop(key)
        proc.gEnv = None

    def refresh(self):
        for proc in self.processors.values():
            proc.parseInputExpr()

            # create a signal instance for each variable that isn't an alias
            for varName in proc.varNames:
                key = hasher.hash_tuple(
                    (proc.dataSource, varName, proc.paramsId))
                value = self._env.get(varName)

                # ensure varName is not aliased, if not, resolve alias (recursively).
                while isinstance(value, str):
                    key = self._env.get(varName)
                    varName = key
                    value = self._env.get(key)

                sig = Signal()
                self._env.update({key: sig})

    def setInputData(self, dataObj: Any, dataSource: str, varName: str, **kwargs):
        signal = self.getSignal(dataSource, varName, **kwargs)
        Translator.new(dataSource).translate(dataObj, signal)

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
