import numpy

import iplotLogging.setupLogger as ls
import re
logger = ls.get_logger(__name__, "DEBUG")


class ProcParsingException(Exception):
    pass


class ExprParser:
    markerIn = "${"
    markerOut = "}"
    keyPrefix = "key"

    def __init__(self):
        self.expr = None
        self.nbarg = 0
        self.compiledVersion = None
        self.result = None
        self.isExpr = False
        self.supportedFcts = self.getFunctionList()
        self.supportedFcts["__builtins__"] = "{}"
        self.localDict = {}
        self.vardict = {}
        self.counter = 0

    def replaceVar(self,expr):
        stop=False
        newexpr=expr
        ##protect the code against infinite loop in case of...
        counter=0
        while not stop:

            if newexpr.find(self.markerIn)==-1  or newexpr.find(self.markerOut) == -1 :
                break
            var = newexpr[newexpr.find(self.markerIn)+len(self.markerIn):newexpr.find(self.markerOut)]
            if var not in self.vardict.keys():
                self.vardict[var] = self.keyPrefix+str(self.counter)
                self.counter = self.counter+1
                newexpr = newexpr.replace(
                    self.markerIn+var+self.markerOut, self.vardict[var])
                logger.debug("newexpr=%s and newkey=%s", newexpr, var)
            counter=counter+1
            if counter >self.nbarg:
                raise ProcParsingException("Invalid expression syntax ",expr)

        return newexpr

    def clearExpr(self, expr):
        self.expr = None
        self.compiledVersion = None
        self.result = None
        self.isExpr = False
        self.localDict = {}
        self.vardict = {}
        self.counter = 0
        self.nbarg = 0

    def isSyntaxValid(self,expr):
        ##make sure we have the following order ${ } ${ } otherwise fail
        isValid = False
        mInpos=[]
        i=0
        mOutpos=[]
        stop=False
        nexpr=expr
        mInpos = [m.start() for m in re.finditer('\${', nexpr)]
        mOutpos = [m.start() for m in re.finditer('}', nexpr)]
        if len(mInpos) != len(mOutpos):
            logger.error("Invalid expression %s, variable should be ${varname} ", nexpr)
            return isValid
        self.nbarg = len(mInpos)
        for i in range(len(mInpos)-2):
            if mOutpos[i]<mInpos[i+1] and mOutpos[i]>mInpos[i]:
                continue
            else:
                logger.error("Invalid expression %s, variable should be ${varname1}  ${varname2}", nexpr)
                return isValid
        isValid=True
        return isValid

    def setExpr(self, expr):
        if expr.find(self.markerIn) == -1 and expr.find(self.markerOut) == -1:
            self.expr = expr
            self.isExpr = False
        else:
            if not self.isSyntaxValid(expr):
                raise ProcParsingException("Invalid expression, variable should be ${varname}")
            else:
                self.expr = self.replaceVar(expr)
                self.isExpr = True
                try:
                    self.validatePreExpr()
                    logger.debug("after validate pre ")
                    self.compiledVersion = compile(
                        self.expr, "<string>", "eval")
                    logger.debug("before validate post")
                    self.validatePostExpr()
                except SyntaxError as se:
                    logger.error("got syntax exc %s", se)
                    raise ProcParsingException("Invalid expression")
                except ValueError as ve:
                    logger.error("got parsing exc %s", ve)
                    raise ProcParsingException("Invalid expression")

    def validatePreExpr(self):
        # to avoid cpu tank we disable ** operator
        if self.expr.find("**") != -1 or self.expr.find("for ") != -1 or self.expr.find("if ") != -1:
            logger.debug("find pre validate check 1 %s ", self.expr)
            raise ProcParsingException("Invalid expression")
        if self.expr.find("__") != -1 or self.expr.find("[]") != -1 or self.expr.find("()") != -1 or self.expr.find("{}") != -1:
            logger.debug("find pre validate check 2 %s", self.expr)
            raise ProcParsingException("Invalid expression")

    def validatePostExpr(self):
        # to do put a timeout on the compile and eval
        # print(self.supportedFcts)
        if self.compiledVersion:
            for name in self.compiledVersion.co_names:
                if name not in self.supportedFcts and name not in self.vardict.values():
                    logger.debug("post and name=%s", name)
                    raise ProcParsingException("Invalid expression")

    def getFunctionList(self):
        from inspect import getmembers, isfunction
        # power and some other are instances of ufunc we don  get them with isfunction
        functions_list = [o for o in getmembers(numpy) if isfunction(
            o[1]) or isinstance(o[1], numpy.ufunc)]
        return dict(functions_list)

    def substituteExpr(self, valMap):
        for k in valMap.keys():
            if self.vardict.get(k):
                self.localDict[self.vardict[k]] = valMap[k]

    def evalExpr(self):
        if self.compiledVersion is not None:
            try:
                #logger.debug("eval exception ")
                self.result = eval(self.compiledVersion,
                                   self.supportedFcts, self.localDict)
            except ValueError as ve:
                logger.error("Value error  %s", ve)
                raise ProcParsingException("Invalid expression")
            except TypeError as te:
                logger.error("Type error  %s", te)
                raise ProcParsingException("Invalid expression")
