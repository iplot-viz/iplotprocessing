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
DEFAULT_PYTHON_MODULES_JSON = os.path.join(os.getenv('IPLOT_PMODULE_PATH', default=ROOT), 'default_modules.json')

DEFAULT_MODULES = "modules"
USER_MODULES = "user_modules"


class Parser:
    """
        This class has been designed following the Singleton design pattern in order to guarantee the existence of a
        single instance of the class in the application.
        This avoids the injection and continuous loading of the modules that are imported by the user when processing
        the different expressions.
    """

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
            self.locals = {}
            self.var_map = {}
            self._var_counter = 0

            self.config = {DEFAULT_MODULES: [], USER_MODULES: []}
            self._access_to_config = True
            self.init_modules()

    def has_access_to_config(self):
        return self._access_to_config

    def load_config_from_json(self):
        # Load json configuration file
        try:
            with open(DEFAULT_PYTHON_MODULES_JSON, 'r') as file:
                config = json.load(file)
                # Keys check
                if DEFAULT_MODULES in config:
                    self.config[DEFAULT_MODULES] = config[DEFAULT_MODULES]
                if USER_MODULES in config:
                    self.config[USER_MODULES] = config[USER_MODULES]

        except (FileNotFoundError, json.JSONDecodeError):
            logger.error("The JSON file does not exist or is not in a valid format. Creating a new one...")
            self.write_config_to_json()

    def write_config_to_json(self):
        try:
            # Writing to the configuration file
            with open(DEFAULT_PYTHON_MODULES_JSON, 'w+') as file:
                file.seek(0)
                json.dump(self.config, file, indent=4)
                file.truncate()

            self._access_to_config = True
        except PermissionError:
            # Handling of permissions error
            logger.error("Error: You do not have the necessary permissions to modify the configuration file. "
                         "Change the environment variable: IPLOT_PMODULE_PATH value")
            self._access_to_config = False

    def load_submodules(self, module, parent_name=""):
        self.inject(self.get_member_list(module))

        for name, obj in inspect.getmembers(module):
            full_name = f"{parent_name}.{name}" if parent_name else name

            if inspect.ismodule(obj) and parent_name in obj.__name__:
                self.load_submodules(obj, full_name)
            elif inspect.isclass(obj):
                self.inject(self.get_member_list(obj))

    def load_modules(self, new_module):
        if new_module == "":
            return

        alias = None
        recursive = False
        # Check new module
        if ' as ' in new_module:
            module_parts = new_module.split(' as ')
            module_name = module_parts[0]
            alias = module_parts[1]
        else:
            module_parts = new_module.split('.')
            if module_parts[-1] == '*':
                recursive = True
                module_name = '.'.join(module_parts[:-1])
            else:
                module_name = new_module

        loaded_module = importlib.import_module(module_name)

        self.inject({module_name: loaded_module})
        if alias:
            self.inject({alias: loaded_module})

        if recursive:
            self.load_submodules(loaded_module, module_name)
        else:
            self.inject(self.get_member_list(loaded_module))

    def format_modules(self):
        # The correct format is set before starting to evaluate the modules
        self.load_config_from_json()
        list_default = self.config[DEFAULT_MODULES]
        list_user = self.config[USER_MODULES]
        user_modules = [module for module in list_user if module not in list_default]
        self.config[USER_MODULES] = user_modules
        self.write_config_to_json()

    def init_modules(self):
        self.format_modules()
        all_modules = self.get_modules()
        for module in all_modules:
            try:
                self.load_modules(module)
            except Exception as e:
                logger.error(f"Error loading module {module}: {e}")
                self.remove_module_from_config(module)

    def remove_module_from_config(self, module):
        default_modules = self.config[DEFAULT_MODULES]
        user_modules = self.config.get(USER_MODULES, [])
        if module in default_modules:
            while module in default_modules:
                default_modules.remove(module)
            self.config[DEFAULT_MODULES] = default_modules
        if module in user_modules:
            while module in user_modules:
                user_modules.remove(module)
            self.config[USER_MODULES] = user_modules
        self.write_config_to_json()

    def get_modules(self):
        return self.config[DEFAULT_MODULES] + self.config[USER_MODULES]

    def add_module_to_config(self, new_module):
        default_modules = self.config.get(DEFAULT_MODULES, [])
        user_modules = self.config.get(USER_MODULES, [])
        if new_module not in user_modules and new_module not in default_modules:
            self.config[USER_MODULES].append(new_module)
            self.write_config_to_json()

    def get_total_default_modules(self):
        return len(self.config[DEFAULT_MODULES])

    def reset_modules(self):
        self.config[USER_MODULES] = []
        self.write_config_to_json()

    def clear_modules(self, index):
        modules = self.get_modules()
        default_modules = self.config[DEFAULT_MODULES]
        deleted_index = [i for i in index if i > len(default_modules) - 1]
        result_modules = [i for j, i in enumerate(modules) if j not in deleted_index and j > len(default_modules) - 1]
        self.config[USER_MODULES] = result_modules
        self.write_config_to_json()
        return deleted_index

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

    @staticmethod
    def get_var_expression(expr: str):
        import re
        matches = re.findall(r'\$\{.*?\}', expr)
        variables = []
        for exp in matches:
            marker_in_pos = exp.find(Parser.marker_in)
            marker_out_pos = exp.find(Parser.marker_out)
            var = exp[marker_in_pos + len(Parser.marker_in):marker_out_pos]
            variables.append(var)

        return variables
