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
import importlib.util
import os
import site
import sys
import sysconfig
import threading

logger = setupLogger.get_logger(__name__, "INFO")


def _normalized(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


# The folders of Python and of the installed packages: a module found there is never imported again (see
# Parser.reload_module).
_INSTALLED = {_normalized(path) for path in [path for name, path in sysconfig.get_paths().items()
                                             if name in ('stdlib', 'platstdlib', 'purelib', 'platlib')]
              + site.getsitepackages() + [site.getusersitepackages()]}


def _folder_of(path: str, folders: typing.List[str]) -> typing.Optional[str]:
    """The folder of the path, out of `folders`, a file was found in: the deepest that holds it."""
    path = _normalized(path)
    return max((folder for folder in folders if path.startswith(os.path.join(folder, ''))), key=len, default=None)


def _location(name: str) -> typing.Optional[str]:
    """Where the top-level package of a module is found: its file, or its folder for a package without one."""
    try:
        spec = importlib.util.find_spec(name.partition('.')[0])
    except (ImportError, ValueError):
        return None
    if spec is None:
        return None
    return spec.origin if spec.has_location else next(iter(spec.submodule_search_locations or ()), None)

ParserT = typing.TypeVar("ParserT", bound="Parser")

EXEC_PATH = __file__
ROOT = os.path.dirname(EXEC_PATH)
DEFAULT_PYTHON_MODULES_JSON = os.path.join(os.getenv('IPLOT_PMODULE_PATH', default=ROOT), 'default_modules.json')

DEFAULT_MODULES = "modules"
USER_MODULES = "user_modules"


class SignalProxy(ProcessingSignal):

    def __init__(self, dict_result=None, env_alias_map=None, envelope: bool = False):
        super().__init__()
        if dict_result is not None:
            if envelope:
                self.alias_map.clear()
                self.alias_map.update(env_alias_map)
                self.data_store.clear()
                self.data_store.append(dict_result["time"])
                self.data_store.append(dict_result["dmin"])
                self.data_store.append(dict_result["dmax"])
                self.data_store.append(dict_result["davg"])
            else:
                self.data_store[0] = dict_result["time"]
                self.data_store[1] = dict_result["data"]


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

    pattern = re.compile(
        r'^\s*(?:from\s+(?P<module_path>[a-zA-Z0-9_.]*)\s+)?'  # from XX
        r'(?:import\s+)?(?P<module>[a-zA-Z0-9_.*]*)'  # import YY
        r'(?:\s+as\s+(?P<alias>[a-zA-Z0-9_.]*))?\s*$'  # as alias
    )

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
            # The members injected, as those of the signals before they are evaluated: they stay when the members of
            # the user modules change (see _rebuild_namespace).
            self._injected = {}
            self._injecting = threading.Lock()

            self._add(Parser.get_member_list(ProcessingSignal))
            self._add(Parser.get_member_list(BufferObject))
            self._add(Parser.add_alias_map_envelope())
            self._add(Parser.add_alias_map_contour())
            self.locals = {}
            self.var_map = {}
            self._var_counter = 0

            self.config = {DEFAULT_MODULES: [], USER_MODULES: []}
            self._access_to_config = True
            # The modules of the user each module of the configuration brought into sys.modules, by module.
            self._brought: typing.Dict[str, typing.Set[str]] = {}
            # The members of the parser and of the default modules: what the namespace is built again from.
            self._base_members = {}
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
        self._add(self._members_of(module, parent_name))

    def _members_of(self, module, parent_name="", members: dict = None) -> dict:
        """The members of a module, and those of its submodules and of their classes."""
        members = {} if members is None else members
        members.update(self.get_member_list(module))

        for name, obj in inspect.getmembers(module):
            full_name = f"{parent_name}.{name}" if parent_name else name

            if inspect.ismodule(obj) and parent_name in obj.__name__:
                self._members_of(obj, full_name, members)
            elif inspect.isclass(obj):
                members.update(self.get_member_list(obj))
        return members

    def load_modules(self, new_module):
        self._add(self._import(new_module))

    def _import(self, entry: str) -> dict:
        """The members a module of the configuration gives expressions, imported if it isn't yet (see _credit)."""
        module_name, alias, recursive = self._parse(entry)
        before = set(sys.modules)
        try:
            loaded_module = importlib.import_module(module_name)
            members = {module_name: loaded_module}
            if alias:
                members[alias] = loaded_module
            members.update(self._members_of(loaded_module, module_name) if recursive
                           else self.get_member_list(loaded_module))
            return members
        finally:
            self._credit(entry, module_name, before)

    def _parse(self, entry: str) -> typing.Tuple[str, typing.Optional[str], bool]:
        """The module an entry of the configuration imports, its alias, and whether expressions also take the members
        of its submodules."""
        match = self.pattern.match(entry)
        if not match:
            raise ValueError(f"Invalid import syntax: '{entry}'")
        module_path, module, alias = match.group('module_path', 'module', 'alias')
        module_name = '.'.join([module_path, module]) if module_path else module

        # Handle wildcard import
        module_parts = module_name.split('.')
        if module_parts[-1] == '*':
            return '.'.join(module_parts[:-1]), alias, True
        return module_name, alias, not module_path and bool(module)

    def _credit(self, entry: str, module_name: str, before: typing.Set[str]):
        """Credit a module of the configuration with the modules of files of the user it brought into sys.modules, which
        are taken out of it to import the module again or remove it: it and its submodules, and those it imported first
        that are found in its folder of the path. Those of Python, of the installed packages and of other folders of the
        path, as the packages on PYTHONPATH, are not."""
        folders = [_normalized(folder) for folder in sys.path]
        location = _location(module_name)
        folder = location and _folder_of(location, folders)
        if not folder or folder in _INSTALLED:
            return

        def found_there(module) -> bool:
            path = getattr(module, '__file__', None)
            return bool(path) and _folder_of(path, folders) == folder

        modules = dict(sys.modules)
        own = {name for name in modules if name == module_name or name.startswith(module_name + '.')}
        self._brought.setdefault(entry, set()).update(
            name for name in own | (modules.keys() - before) if found_there(modules[name]))

    def format_modules(self):
        # The correct format is set before starting to evaluate the modules
        self.load_config_from_json()
        list_default = self.config[DEFAULT_MODULES]
        list_user = self.config[USER_MODULES]
        # Before rewriting the user modules, check if the formatting has to be done
        if bool(set(list_default) & set(list_user)):
            user_modules = [module for module in list_user if module not in list_default]
            self.config[USER_MODULES] = user_modules
            self.write_config_to_json()

    def init_modules(self):
        self.format_modules()
        self._load_or_drop(self.config[DEFAULT_MODULES])
        self._base_members = dict(self._supported_members)
        self._load_or_drop(self.config[USER_MODULES])

    def _load_or_drop(self, modules: typing.List[str]):
        """Load modules of the configuration, and drop from it those that fail to."""
        for module in list(modules):
            try:
                self.load_modules(module)
            except Exception as e:
                logger.error(f"Error loading module {module}: {e}")
                self.remove_module_from_config(module)

    def reload_module(self, module: str):
        """Import the user modules of the configuration again, as their files are now, and let expressions use them so:
        all of them, as they may share files, as a helper two of them import. `module` goes first: if it fails, as for
        an error in its code, they all stay as they were and the error is raised. Another one that fails stays as it
        was."""
        brought, self._brought = self._brought, {}
        taken = self._forget(set().union(*brought.values()))
        try:
            self._import(module)
        except Exception:
            for name in self._brought.pop(module, set()):
                sys.modules.pop(name, None)
            sys.modules.update(taken)
            self._brought = brought
            raise
        self._rebuild_namespace(brought, taken)

    def _unload(self, modules: typing.Iterable[str]):
        """Take user modules no longer in the configuration out of expressions, and out of memory."""
        for module in modules:
            self._forget(self._brought.pop(module, set()))
        self._rebuild_namespace()

    @staticmethod
    def _forget(names: typing.Iterable[str]) -> dict:
        """Take modules out of sys.modules, so that the next import reads their files again; and their compiled code,
        which Python only reads again when the size or the second of a file changed. Returns the modules taken out."""
        taken = {name: sys.modules.pop(name) for name in names if name in sys.modules}
        for value in taken.values():
            try:
                os.remove(value.__cached__)
            except (AttributeError, TypeError, OSError):
                pass
        importlib.invalidate_caches()
        return taken

    def _rebuild_namespace(self, brought: dict = None, taken: dict = None):
        """Build what expressions use again, apart, and then put it in place, so that an expression evaluated meanwhile
        finds all it found: the members of the parser and of the default modules, those of the user modules of the
        configuration, then those injected. A user module that can't be imported again gets back its modules of
        before, those `taken` out that `brought` credited it with, and stays as it was."""
        members = dict(self._base_members)
        for module in list(self.config[USER_MODULES]):
            try:
                members.update(self._import(module))
            except Exception as e:
                kept = self._as_it_was(module, brought or {}, taken or {})
                if kept is None:
                    logger.error(f"Error loading module {module}: {e}")
                    continue
                logger.warning(f"Module {module} stays as it was, as importing it again failed: {e}")
                members.update(kept)
        with self._injecting:
            members.update(self._injected)
            self._supported_members, self._supported_member_names = members, set(members)

    def _as_it_was(self, module: str, brought: dict, taken: dict) -> typing.Optional[dict]:
        """The members of a user module from its modules of before, put back in sys.modules; None if it had none."""
        old = {name: taken[name] for name in brought.get(module, set()) if name in taken and name not in sys.modules}
        if not old:
            return None
        sys.modules.update(old)
        self._brought.setdefault(module, set()).update(old)
        try:
            return self._import(module)
        except Exception:
            return None

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

    def get_modules_names(self):
        module_list = self.config[DEFAULT_MODULES] + self.config[USER_MODULES]
        result = []
        for module in module_list:
            match = self.pattern.match(module)
            data = match.groupdict()
            module_path = data['module_path']
            module_name = data['module']
            if module_path:
                module_name = '.'.join([module_path, module_name])
            result.append(module_name)

        return result

    def add_module_to_config(self, new_module):
        default_modules = self.config.get(DEFAULT_MODULES, [])
        user_modules = self.config.get(USER_MODULES, [])
        if new_module not in user_modules and new_module not in default_modules:
            self.config[USER_MODULES].append(new_module)
            self.write_config_to_json()

    def get_total_default_modules(self):
        return len(self.config[DEFAULT_MODULES])

    def reset_modules(self):
        removed = self.config[USER_MODULES]
        self.config[USER_MODULES] = []
        self.write_config_to_json()
        self._unload(removed)

    def clear_modules(self, index):
        modules = self.get_modules()
        default_modules = self.config[DEFAULT_MODULES]
        deleted_index = [i for i in index if i > len(default_modules) - 1]
        result_modules = [i for j, i in enumerate(modules) if j not in deleted_index and j > len(default_modules) - 1]
        removed = [module for module in self.config[USER_MODULES] if module not in result_modules]
        self.config[USER_MODULES] = result_modules
        self.write_config_to_json()
        self._unload(removed)
        return deleted_index

    @property
    def supported_members(self) -> dict:
        return self._supported_members

    def inject(self, members: dict) -> ParserT:
        with self._injecting:
            self._injected.update(members)
            self._add(members)
        return self

    def _add(self, members: dict):
        self._supported_members.update(members)
        self._supported_member_names.update(members)

    def replace_var(self, expr: str, envelope: bool = False, idx: int = None) -> str:
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
            check = new_expr[marker_out_pos + 1:]
            add_data = False

            if var not in self.var_map.keys():
                if not check.startswith(('.data', '.time', '.dmin', '.dmax', '.davg')):
                    add_data = True

                self.var_map[var] = self.prefix + str(self._var_counter)
                self._var_counter = self._var_counter + 1
                match = self.marker_in + var + self.marker_out
                replc = self.var_map[var]
                if add_data:
                    if envelope:
                        if idx == 1:
                            replc += '.dmin'
                        elif idx == 2:
                            replc += '.dmax'
                        else:
                            replc += '.davg'
                    else:
                        replc += '.data'
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
            logger.error(f"Invalid expression {expr}, variable should be ${{varname}}")
            return False

        self.marker_in_count = len(marker_in_pos)
        for i in range(len(marker_in_pos) - 2):
            if marker_in_pos[i + 1] > marker_out_pos[i] > marker_in_pos[i]:
                continue
            else:
                return False

        return True

    def set_expression(self, expr: str, is_expression: bool = False, envelope: bool = False,
                       idx: int = None) -> ParserT:
        if expr.find(self.marker_in) == -1 and expr.find(self.marker_out) == -1 and not is_expression:
            self.expression = expr
            self.is_valid = False
        else:
            if not self.is_syntax_valid(expr):
                raise InvalidExpression(f"Invalid expression {expr}, variable should be '${{varname1}}  ${{varname2}}'")
            else:
                self.expression = self.replace_var(expr, envelope, idx)
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
                    self._compiled_obj = compile(self.expression, "<string>", "eval")
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

    @staticmethod
    def add_alias_map_envelope():
        alias_map = {
            'time': {'idx': 0, 'independent': True},
            'dmin': {'idx': 1},
            'dmax': {'idx': 2},
            'davg': {'idx': 3}
        }

        return alias_map

    @staticmethod
    def add_alias_map_contour():
        alias_map = {
            'r': {'idx': 0, 'independent': True},
            'z': {'idx': 1, 'independent': True},
            'psi': {'idx': 2}
        }

        return alias_map

    def substitute_var(self, val_map, dict_result=None, env_alias_map=None, envelope: bool = False) -> ParserT:
        for k in val_map.keys():
            if self.var_map.get(k):
                if not dict_result:
                    # Bind the signal directly so ${alias}.data resolves to the signal's
                    # actual BufferObject through its alias_map. Wrapping in SignalProxy here
                    # would store the signal itself in data_store and break .data/.time access
                    # for dependencies whose time axes do not require realignment.
                    self.locals[self.var_map[k]] = val_map[k]
                else:
                    # Check for self in case if self.data_store[2]
                    if k not in dict_result.keys():
                        self.locals[self.var_map[k]] = val_map[k]
                    else:
                        self.locals[self.var_map[k]] = SignalProxy(dict_result[k], env_alias_map, envelope)
        return self

    def eval_expr(self) -> ParserT:
        if self._compiled_obj is not None:
            try:
                # logger.debug("eval exception ")
                self.result = eval(self._compiled_obj, self.supported_members, self.locals)
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
