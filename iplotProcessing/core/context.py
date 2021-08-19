import typing
from iplotProcessing.core.processor import Processor
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools.hasher import hash_tuple
from iplotProcessing.tools.parsers import ExprParser


class Context:
    def __init__(self) -> None:
        self._processors = {}
        self._env = {}

    def resolve(self, sourceId: str, name: str) -> Signal:
        hcode = hash_tuple((sourceId, name))
        return self._env.get(hcode)
    
    def get(self, name: str) -> str:
        return self._env.get(name)

    def update(self, key: str, value: typing.Union[str, Signal]):
        if not isinstance(value, str) and not isinstance(value, Signal):
            raise AttributeError("value must be either a string or a Signal")
        self._env.update({key: value})

    def register(self, proc: Processor):
        if proc is None:
            return

        self.processors.update({id(proc): proc})
        proc.gEnv = self.env

    def deRegister(self, proc: Processor):
        if proc is None:
            return

        self.processors.pop(id(proc))
        proc.gEnv = None

    def refresh(self):
        for proc in self.processors.values():
            parser = ExprParser()
            parser.setExpr(proc.inputExpr)
            
            # create a signal instance for each variable that isn't an alias
            for varName in parser.vardict.keys():
                hcode = hash_tuple((proc.sourceId, varName))
                if self.get(varName) is None:
                    self._env.update({hcode: Signal()})


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
        if not isinstance(val, dict):
            raise AttributeError(
                "Restricted access. Cannot assign non dictionary object to environment.")
        self._env = val

        for proc in self.processors.values():
            if isinstance(proc, Processor):
                proc.gEnv = self._env
