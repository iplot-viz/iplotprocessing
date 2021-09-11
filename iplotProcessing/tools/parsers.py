from inspect import getmembers
import numpy
import re

from iplotProcessing.common.errors import InvalidExpression
import iplotLogging.setupLogger as ls

logger = ls.get_logger(__name__, "DEBUG")


class Parser:
    marker_in = "${"
    marker_out = "}"
    prefix = "key"
    date_time_unit_pattern = r"(\d+)([YMWDhms]\b|ms|us|ns|ps|fs|as)"

    def __init__(self):
        self.expression = ""
        self.marker_in_count = 0
        self._compiled_obj = None
        self.result = None
        self.is_valid = False
        self.has_time_units = False
        self.supported_members = self.get_member_list(numpy)
        self.supported_members.update({"np": numpy})
        self.supported_members.update(self.get_member_list(numpy.ndarray))
        self.supported_members["__builtins__"] = "{}"
        self.locals = {}
        self.var_map = {}
        self._var_counter = 0

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

            counter = counter+1

            if counter > self.marker_in_count:
                raise InvalidExpression(f"Invalid expression syntax {expr}")

        return new_expr

    def clear_expr(self):
        self.expression = ""
        self._compiled_obj = None
        self.result = None
        self.is_valid = False
        self.locals.clear()
        self.var_map.clear()
        self._var_counter = 0
        self.marker_in_count = 0

    def is_syntax_valid(self, expr: str) -> bool:
        # make sure we have the following order ${ } ${ } otherwise fail
        marker_in_pos = []
        marker_out_pos = []

        marker_in_pos = [m.start() for m in re.finditer('\${', expr)]
        marker_out_pos = [m.start() for m in re.finditer('}', expr)]

        if len(marker_in_pos) != len(marker_out_pos):
            logger.error(
                "Invalid expression %s, variable should be ${varname} ", expr)
            return False

        self.marker_in_count = len(marker_in_pos)
        for i in range(len(marker_in_pos) - 2):
            if marker_out_pos[i] < marker_in_pos[i + 1] and marker_out_pos[i] > marker_in_pos[i]:
                continue
            else:
                return False

        return True

    def set_expression(self, expr: str):
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

    def validate_pre_compile(self):
        logger.debug("Validating prior to compilation")
        # to avoid cpu tank we disable ** operator
        if self.expression.find("**") != -1 or self.expression.find("for ") != -1 or self.expression.find("if ") != -1:
            logger.debug(f"pre validate check 1 {self.expression}")
            raise InvalidExpression("Invalid expression")
        if self.expression.find("__") != -1 or self.expression.find("[]") != -1 or self.expression.find("()") != -1 or self.expression.find("{}") != -1:
            logger.debug(f"pre validate check 2 {self.expression}")
            raise InvalidExpression("Invalid expression")

    def validate_post_compile(self):
        logger.debug("Validating post compilation")
        # to do put a timeout on the compile and eval
        # print(self.supported_members)
        if self._compiled_obj:
            for name in self._compiled_obj.co_names:
                if name not in [*self.supported_members, *self.var_map.values()]:
                    raise InvalidExpression(f"Undefined name {name}")

    def get_member_list(self, parent):
        functions_list = [o for o in getmembers(parent)]
        return dict(functions_list)

    def substitute_var(self, val_map):
        for k in val_map.keys():
            if self.var_map.get(k):
                self.locals[self.var_map[k]] = val_map[k]

    def eval_expr(self):
        if self._compiled_obj is not None:
            try:
                #logger.debug("eval exception ")
                self.result = eval(self._compiled_obj,
                                   self.supported_members, self.locals)
            except ValueError as ve:
                logger.exception(ve)
                raise InvalidExpression(f"Value error {ve}")
            except TypeError as te:
                logger.exception(te)
                raise InvalidExpression(f"Type error {te}")
