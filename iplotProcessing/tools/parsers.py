# Description: Parse, Eval expression strings in the python interpreter within a user-provided environment
# Author: Abadie Lana
# Changelog:
#   Sept 2021: Added generic get_member_list function to inject outsider functions/attributes [Jaswant Sai Panchumarti]
import inspect
import json
from inspect import getmembers
import typing
import re
from iplotProcessing.common import InvalidExpression, InvalidVariable, DATE_TIME, PRECISE_TIME
from iplotProcessing.core import BufferObject
from iplotProcessing.core import Signal as ProcessingSignal
from iplotLogging import setupLogger
import importlib
import os

logger = setupLogger.get_logger(__name__, "INFO")

ParserT = typing.TypeVar("ParserT", bound="Parser")

EXEC_PATH = __file__
ROOT = os.path.dirname(EXEC_PATH)
DEFAULT_PYTHON_MODULES_JSON = os.path.join(ROOT, 'pythonmodulesdefault.json')


class Parser:
    marker_in = "${"
    marker_out = "}"
    prefix = "key"
    date_time_unit_pattern = rf"(\d+)([{''.join(DATE_TIME)}]\b|{'|'.join(PRECISE_TIME)})"

    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Parser, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.expression = ""
            self.marker_in_count = 0
            self._compiled_obj = None
            self.result = None
            self.is_valid = False
            self.has_time_units = False
            self._supported_member_names = set()
            self._supported_members = dict()

            self.inject(Parser.get_member_list(ProcessingSignal))
            self.inject(Parser.get_member_list(BufferObject))

            self.init_modules()

            self.locals = {}
            self.var_map = {}
            self._var_counter = 0

    def add_module(self, module, recursive, parent_name=""):
        self.inject(self.get_member_list(module))

        if not recursive:
            return

        for name, obj in inspect.getmembers(module):
            full_name = f"{parent_name}.{name}" if parent_name else name

            if inspect.ismodule(obj) and parent_name in obj.__name__:
                self.add_module(obj, recursive, full_name)
            elif inspect.isclass(obj):
                self.inject(self.get_member_list(obj))

    def load_modules(self, new_module):
        if new_module == "":
            return

        # Check new module
        if ' as ' in new_module:
            module_parts = new_module.split(' as ')
            module_name = module_parts[0]
            alias = module_parts[1]
        else:
            module_parts = new_module.split('.')
            module_name = module_parts[0]
            alias = None

        submodule_name = '.'.join(module_parts[1:])

        recursive = len(module_parts) != 1 and not alias

        if submodule_name == '*':
            loaded_module = importlib.import_module(module_name)
        elif alias:
            loaded_module = importlib.import_module(module_name)
        else:
            loaded_module = importlib.import_module(new_module)

        self.add_module(loaded_module, recursive)

        if not recursive:
            self.inject({module_name: loaded_module})
            if alias:
                self.inject({alias: loaded_module})

    def init_modules(self):
        modules = self.get_modules()
        for module in modules:
            try:
                self.load_modules(module)
            except Exception as e:
                logger.error(f"Error loading module {module}: {e}")
                self.remove_module_to_config(module)

    @staticmethod
    def remove_module_to_config(module):
        with open(DEFAULT_PYTHON_MODULES_JSON, 'r+') as file:
            config = json.load(file)
            modules = config.get('modules', [])
            user_modules = config.get('user_modules', [])
            if module in modules:
                modules.remove(module)
                config['modules'] = modules
            if module in user_modules:
                user_modules.remove(module)
                config['user_modules'] = user_modules
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()

    def add_module_to_config(self, new_module):
        # Write new module in configuration file
        with open(DEFAULT_PYTHON_MODULES_JSON, 'r+') as file:
            config = json.load(file)
            modules = config.get('user_modules', [])
            if new_module not in modules:
                modules.append(new_module)
                config['user_modules'] = modules
                file.seek(0)
                json.dump(config, file, indent=4)
                file.truncate()

    @staticmethod
    def get_modules():
        # Import modules from conf file
        with open(DEFAULT_PYTHON_MODULES_JSON, 'r') as file:
            config = json.load(file)
            modules = list(dict.fromkeys(config.get('modules', []) + config.get('user_modules', [])))
            return modules

    @staticmethod
    def reset_modules():
        with open(DEFAULT_PYTHON_MODULES_JSON, 'r+') as file:
            config = json.load(file)
            modules = config.get('modules', [])
            config['user_modules'] = []
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()
            return len(modules)

    @staticmethod
    def clear_modules(index):
        with open(DEFAULT_PYTHON_MODULES_JSON, 'r+') as file:
            config = json.load(file)
            modules = config.get('user_modules', [])
            default_modules = config.get('modules', [])
            valid_index = [i for i in index if i > len(default_modules) - 1]
            result_modules = [i for j, i in enumerate(modules) if j not in valid_index]
            config['user_modules'] = result_modules
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()
            return valid_index

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
        self.var_map = {}
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
        return dict(getmembers(parent))

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
