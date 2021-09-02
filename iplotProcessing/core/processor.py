import typing
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher, parsers
from iplotLogging import setupLogger as sl
from numpy.core.fromnumeric import var

logger = sl.get_logger(__name__, "INFO")

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

    def isComposite(self) -> bool:
        return len(self.varNames) > 1

    def setParams(self, dataSource: str, inputExpr: str, **kwargs):
        if not isinstance(dataSource, str): # reset nan from csv (if empty, pandas makes it nan)
            dataSource = ""
        self.dataSource = dataSource
        if not isinstance(inputExpr, str): # reset nan from csv (if empty, pandas makes it nan)
            inputExpr = ""
        self.inputExpr = inputExpr
        self.params = kwargs

    def parseInputExpr(self):
        self._varNames.clear()
        parser = parsers.ExprParser()
        parser.setExpr(self.inputExpr)

        if not len(self.inputExpr):
            self._parsedInput = ""
            parser.clearExpr("")
        elif not parser.isExpr:  # for single varname without '${', '}'
            self._parsedInput = parser.markerIn + self.inputExpr + parser.markerOut
            parser.clearExpr("")
            parser.setExpr(self._parsedInput)
        else:
            self._parsedInput = self.inputExpr

        # now replace ascii varnames with the hash codes and aliases with their target hash codes
        for varName in parser.vardict.keys():
            hashCode = hasher.hash_tuple((self.dataSource, varName, self.paramsId))

            aliasTmp = None
            while True:
                # Try Signal
                value = self.gEnv.get(hashCode)
                if isinstance(value, Signal):
                    break
                # Try alias
                if aliasTmp is None:
                    aliasRef = self.gEnv.get(varName)
                else:
                    aliasRef = self.gEnv.get(aliasTmp)
                if isinstance(aliasRef, str):
                    hashCode = aliasRef
                    aliasTmp = aliasRef
                    continue
                else:
                    break

            self._parsedInput = self._parsedInput.replace(varName, hashCode)
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

        hashCode = hasher.hash_code(self, ["dataSource", "inputExpr", "paramsId"])
        self.gEnv[hashCode] = self.output

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

        for varName in parser.vardict.keys():
            hashCode = hasher.hash_tuple((self.dataSource, varName, self.paramsId))
            aliasTmp = None

            while True:
                # Try Signal
                value = self.gEnv.get(hashCode)
                if isinstance(value, Signal):
                    self.lEnv.update({varName: value})
                    break
                # Try alias
                if aliasTmp is None:
                    aliasRef = self.gEnv.get(varName)
                else:
                    aliasRef = self.gEnv.get(aliasTmp)
                if isinstance(aliasRef, str):
                    hashCode = aliasRef
                    aliasTmp = aliasRef
                    continue
                else:
                    break

        parser.substituteExpr(self.lEnv)
        parser.evalExpr()
        if isinstance(parser.result, Signal):
            return parser.result.data_primary
        else:
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
