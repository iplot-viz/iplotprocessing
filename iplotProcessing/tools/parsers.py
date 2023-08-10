# Description: Parse, Eval expression strings in the python interpreter within a user-provided environment
# Author: Abadie Lana
# Changelog:
#   Sept 2021: Added generic get_member_list function to inject outsider functions/attributes [Jaswant Sai Panchumarti]

from inspect import getmembers
import typing
import numpy
import re
import scipy.signal
from iplotProcessing.common import InvalidExpression, InvalidVariable, DATE_TIME, PRECISE_TIME
from iplotLogging import setupLogger

logger = setupLogger.get_logger(__name__, "INFO")

ParserT = typing.TypeVar("ParserT", bound="Parser")


class Parser:
    marker_in = "${"
    marker_out = "}"
    prefix = "key"
    date_time_unit_pattern = rf"(\d+)([{''.join(DATE_TIME)}]\b|{'|'.join(PRECISE_TIME)})"

    def __init__(self):
        self.expression = ""
        self.marker_in_count = 0
        self._compiled_obj = None
        self.result = None
        self.is_valid = False
        self.has_time_units = False
        self._supported_member_names = set()
        self._supported_members = dict()
        self.inject(self.get_member_list(numpy))
        self.inject(self.get_member_list(numpy.add))
        self.inject(self.get_member_list(numpy.ndarray))
        self.inject(self.get_member_list(scipy.signal))
        self.inject({"numpy": numpy})
        self.inject({"np": numpy})
        self.inject({"sp.signal": scipy.signal})
        self.inject({"__builtins__": '{}'})
        self.locals = {}
        self.var_map = {}
        self._var_counter = 0

    @property
    def supported_members(self) -> dict:
        return self._supported_members

    def inject(self, members: dict) -> ParserT:
        self._supported_members.update(members)
        for k in members.keys():
            self._supported_member_names.add(k)
        return self

    def replace_var(self, expr: str) -> str:
        new_expr = expr
        # protect the code against infinite loop in case of...
        counter = 0
        while True:

            if new_expr.find(self.marker_in) == -1 or new_expr.find(self.marker_out) == -1:
                break
            marker_in_pos = new_expr.find(self.marker_in)
            marker_out_pos = new_expr.find(self.marker_out)
            var = new_expr[marker_in_pos + len(self.marker_in):marker_out_pos]

            if var not in self.var_map.keys():
                self.var_map[var] = self.prefix + str(self._var_counter)
                self._var_counter = self._var_counter + 1
                match = self.marker_in + var + self.marker_out
                replc = self.var_map[var]
                new_expr = new_expr.replace(match, replc)
                logger.debug(f"new_expr = {new_expr} and new_key = {var}")

            counter = counter + 1

            if counter > self.marker_in_count:
                raise InvalidExpression(f"Invalid expression syntax {expr}")

        return new_expr

    def clear_expr(self) -> ParserT:
        self.expression = ""
        self._compiled_obj = None
        self.result = None
        self.is_valid = False
        self.has_time_units = False
        self.locals.clear()
        self.var_map.clear()
        self._var_counter = 0
        self.marker_in_count = 0

        return self

    def is_syntax_valid(self, expr: str) -> bool:
        # make sure we have the following order ${ } ${ } otherwise fail
        marker_in_pos = [m.start() for m in re.finditer(r'\${', expr)]
        marker_out_pos = [m.start() for m in re.finditer('}', expr)]

        if len(marker_in_pos) != len(marker_out_pos):
            logger.error(
                "Invalid expression %s, variable should be ${varname} ", expr)
            return False

        self.marker_in_count = len(marker_in_pos)
        for i in range(len(marker_in_pos) - 2):
            if marker_in_pos[i + 1] > marker_out_pos[i] > marker_in_pos[i]:
                continue
            else:
                return False

        return True

    def set_expression(self, expr: str) -> ParserT:
        if expr.find(self.marker_in) == -1 and expr.find(self.marker_out) == -1:
            self.expression = expr
            self.is_valid = False
        else:
            if not self.is_syntax_valid(expr):
                raise InvalidExpression(
                    f"Invalid expression {expr}, variable should be '${{varname1}}  ${{varname2}}'")
            else:
                self.expression = self.replace_var(expr)
                self.is_valid = True

                # parse time vector math
                for digit, unit in re.findall(self.date_time_unit_pattern, self.expression):
                    self.has_time_units = True
                    match = f"{digit}{unit}"
                    replc = "np.timedelta64({},'{}')".format(int(digit), unit)
                    logger.debug(f"Replacing '{match}' with '{replc}'")
                    self.expression = self.expression.replace(match, replc)

                try:
                    self.validate_pre_compile()
                    self._compiled_obj = compile(
                        self.expression, "<string>", "eval")
                    self.validate_post_compile()
                except SyntaxError as se:
                    raise InvalidExpression(f"Syntax error {se}")
                except ValueError as ve:
                    raise InvalidExpression(f"Parsing error {ve}")

        return self

    def validate_pre_compile(self):
        logger.debug("Validating prior to compilation")
        # to avoid cpu tank we disable ** operator
        if self.expression.find("**") != -1 or self.expression.find("for ") != -1 or self.expression.find("if ") != -1:
            logger.debug(f"pre validate check 1 {self.expression}")
            raise InvalidExpression("Invalid expression")
        if self.expression.find("__") != -1 or self.expression.find("[]") != -1 or self.expression.find(
                "()") != -1 or self.expression.find("{}") != -1:
            logger.debug(f"pre validate check 2 {self.expression}")
            raise InvalidExpression("Invalid expression")

    def validate_post_compile(self):
        logger.debug("Validating post compilation")
        # to do put a timeout on compile and eval
        # print(self.supported_members)
        if self._compiled_obj:
            for name in self._compiled_obj.co_names:
                if name not in self._supported_member_names and name not in self.var_map.values():
                    raise InvalidExpression(f"Undefined name {name}")

    @staticmethod
    def get_member_list(parent):
        functions_list = [o for o in getmembers(parent)]
        return dict(functions_list)

    def substitute_var(self, val_map) -> ParserT:
        for k in val_map.keys():
            if self.var_map.get(k):
                self.locals[self.var_map[k]] = val_map[k]
        return self

    def eval_expr(self) -> ParserT:
        if self._compiled_obj is not None:
            try:
                # logger.debug("eval exception ")
                self.result = eval(self._compiled_obj,
                                   self.supported_members, self.locals)
            except ValueError as ve:
                raise InvalidExpression(f"Value error {ve}")
            except TypeError as te:
                logger.warning(f"Type error {te}")
                raise InvalidVariable(self.var_map, self.locals)

        return self
