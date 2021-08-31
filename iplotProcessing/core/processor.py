import typing
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher, parsers
from iplotLogging import setupLogger as sl
from numpy.core.fromnumeric import var

logger = sl.get_logger(__name__, "DEBUG")


class Processor:
    def __init__(self):
        self.sourceId = None  # ex: imasuda, codacuda, jet .. etc

        self._inputExpr = None
        self._varNames = set()
        self.output = Signal()

        self.gEnv = {}  # g: global, l: local
        self.lEnv = {"self": self.output}

    def refresh(self):
        self._varNames.clear()
        parser = parsers.ExprParser()
        parser.setExpr(self.inputExpr)

        if not parser.isExpr:  # for single varname without '${', '}'
            inputExpr = parser.markerIn + self.inputExpr + parser.markerOut
            parser.clearExpr("")
            parser.setExpr(inputExpr)
        else:
            inputExpr = self.inputExpr

        # now replace ascii varnames with the hash codes
        for varName in parser.vardict.keys():
            hashcode = hasher.hash_tuple((self.sourceId, varName))
            inputExpr = inputExpr.replace(varName, hashcode)
            self._varNames.add(varName)

        # parse and evaluate the new input expression
        parser.clearExpr("")
        parser.setExpr(inputExpr)
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

    @property
    def varNames(self):
        if not len(self._varNames):
            self.refresh()
        return self._varNames

    @varNames.setter
    def varNames(self, val):
        raise AttributeError("Restricted access. Cannot assign varNames.")