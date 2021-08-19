from iplotProcessing.core.signal import Signal
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "DEBUG")


class Processor:
    def __init__(self):
        self.sourceId = None  # ex: imasuda, codacuda, jet .. etc

        self.gEnv = {}  # g: global
        self.lEnv = {}  # l: local

        self._inputExpr = None
        self.output = Signal()

    @property
    def inputExpr(self):
        return self._inputExpr

    @inputExpr.setter
    def inputExpr(self, val: str):
        if not isinstance(val, str):
            raise AttributeError("Expression is not a string.")
        self._inputExpr = val
