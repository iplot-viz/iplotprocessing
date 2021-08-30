import typing
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher, parsers
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, "DEBUG")


class Processor:
    def __init__(self):
        self.sourceId = None  # ex: imasuda, codacuda, jet .. etc

        self._inputExpr = None
        self.output = Signal()

        self.gEnv = {}  # g: global, l: local
        self.lEnv = {"self": self.output}

    def refresh(self):
        parser = parsers.ExprParser()
        parser.setExpr(self.inputExpr)

        keys = parser.vardict.keys()
        if not parser.isExpr:  # for single varname without '${', '}'
            keys = [self.inputExpr]

        inputExpr = self._inputExpr
        for varName in keys:
            hashcode = hasher.hash_tuple((self.sourceId, varName))
            inputExpr = inputExpr.replace(varName, hashcode)

        parser.clearExpr("")
        parser.setExpr(parser.markerIn + inputExpr + parser.markerOut)
        parser.substituteExpr(self.gEnv)
        parser.evalExpr()

        self.output = parser.result
        self.lEnv.update({"self": self.output})

    def compute(self, expr: str) -> typing.Any:
        # TODO: An expression such as `${self}.time` raises ProcParsingException. This code ignores it.
        if not isinstance(expr, str):
            return

        self.refresh()

        parser = parsers.ExprParser()
        try:
            parser.setExpr(expr)
        except parsers.ProcParsingException:
            pass

        if not parser.isExpr:
            return None

        for varname in parser.vardict.keys():
            key = hasher.hash_tuple((self.sourceId, varname))

            while True:
                value = self.gEnv.get(key)
                aliasRef = self.gEnv.get(varname)
                if isinstance(value, Signal):
                    self.lEnv.update({varname: value})
                    break
                elif isinstance(aliasRef, str):
                    key = aliasRef
                    continue
                else:
                    break

        parser.substituteExpr(self.lEnv)
        parser.evalExpr()
        return parser.result

    @property
    def inputExpr(self):
        return self._inputExpr

    @inputExpr.setter
    def inputExpr(self, val: str):
        if not isinstance(val, str):
            raise AttributeError("Expression is not a string.")
        self._inputExpr = val
