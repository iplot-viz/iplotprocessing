import typing
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher, parsers
from iplotLogging import setupLogger as sl
from numpy.core.fromnumeric import var

logger = sl.get_logger(__name__, "DEBUG")

DEFAULT_PARAMS_ID = "a"


class Processor:
    @staticmethod
    def getParamsId(params: dict):
        return DEFAULT_PARAMS_ID if not len(
            params) else hasher.hash_tuple(tuple(params.values()))

    def __init__(self):
        self.dataSource = None  # ex: imasuda, codacuda, jet .. etc
        self.inputExpr = ""
        self.output = Signal()

        self.params = dict()

        self.gEnv = {}  # g: global, l: local
        self.lEnv = {"self": self.output}

        self._paramsId = DEFAULT_PARAMS_ID
        self._parsedInput = ""
        self._varNames = set()

    def setParams(self, dataSource: str, inputExpr: str, **kwargs):
        self.dataSource = dataSource
        self.inputExpr = inputExpr
        self.params = kwargs

    def parseInputExpr(self):
        self._varNames.clear()
        parser = parsers.ExprParser()
        parser.setExpr(self.inputExpr)

        if not parser.isExpr:  # for single varname without '${', '}'
            self._parsedInput = parser.markerIn + self.inputExpr + parser.markerOut
            parser.clearExpr("")
            parser.setExpr(self._parsedInput)
        else:
            self._parsedInput = self.inputExpr

        # now replace ascii varnames with the hash codes
        for varName in parser.vardict.keys():
            hashcode = hasher.hash_tuple(
                (self.dataSource, varName, self.paramsId))
            self._parsedInput = self._parsedInput.replace(varName, hashcode)
            self._varNames.add(varName)

    def refresh(self):
        # evaluate the new input expression
        parser = parsers.ExprParser()
        parser.clearExpr("")
        parser.setExpr(self._parsedInput)
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
            key = hasher.hash_tuple((self.dataSource, varname))

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
    def paramsId(self):
        return Processor.getParamsId(self.params)

    @paramsId.setter
    def paramsId(self, val):
        raise AttributeError("Restricted access. Cannot assign paramsId.")

    @property
    def varNames(self):
        if not len(self._varNames):
            self.parseInputExpr()
        return self._varNames

    @varNames.setter
    def varNames(self, val):
        raise AttributeError("Restricted access. Cannot assign varNames.")
