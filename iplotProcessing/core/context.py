import typing
from collections import defaultdict
from iplotProcessing.common import getParamsId
from iplotProcessing.core.environment import Environment
from iplotProcessing.core.processor import Processor
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher
from iplotProcessing.translators import Translator


class Context:
    def __init__(self) -> None:
        self._processors = defaultdict(list)
        self._env = Environment()

    def reset(self) -> None:
        while len(self._processors):
            self.deRegister(list(self._processors.values())[-1])
        self._env.clear()
        assert(not len(self.processors))
        assert(not len(self.env))

    def getSignal(self, dataSource: str, name: str, **kwargs) -> typing.Tuple[str, Signal]:
        return self._env.getSignal(dataSource, name, **kwargs)

    def getProcessor(self, dataSource: str, inputExpr: str, **kwargs) -> Processor:
        paramsId = getParamsId(kwargs)
        key = hasher.hash_tuple((dataSource, inputExpr, paramsId))
        return self._processors.get(key)

    def updateAlias(self, dataSource: str, name: str, alias: str, **kwargs):
        self._env.updateAlias(dataSource, name, alias, **kwargs)

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

            if proc.isComposite():
                key = hasher.hash_code(
                    proc, ["dataSource", "inputExpr", "paramsId"])
                self._env.update({key: Signal()})
            else:
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

    def setInputData(self, dataObj: typing.Any, dataSource: str, name: str, **kwargs):
        _, signal = self.getSignal(dataSource, name, **kwargs)
        Translator.new(dataSource).translate(dataObj, signal)

    def getOutputData(self, expression, dataSource: str, name: str, errorHandler=None, **kwargs) -> typing.Any:
        proc = self.getProcessor(dataSource, name, **kwargs)
        return proc.compute(expression, errorHandler)

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
            "Restricted access. Cannot assign an environment. Please work with existing one.")
