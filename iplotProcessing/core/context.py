import time
import typing
import pandas as pd

from iplotProcessing.common.errors import InvalidExpression, InvalidSignalName, UnboundSignal
from iplotProcessing.common.table_parser import get_value
from iplotProcessing.core.environment import Environment
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import parsers
from iplotProcessing.translators import Translator
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="DEBUG")


class Context:
    def __init__(self) -> None:

        self._env = Environment()
        self._data_access_callback = None

        self._build_time = time.time_ns()
        self._mod_time = time.time_ns()

    def reset(self) -> None:

        self._env.clear()
        assert(not len(self.env))

    @property
    def data_access_callback(self):
        return self._data_access_callback

    @data_access_callback.setter
    def data_access_callback(self, val: typing.Callable):

        if not callable(val):
            raise TypeError("Callback is not callable!")
        self._data_access_callback = val

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, val: dict):
        raise AttributeError(
            "Restricted access. Cannot assign an environment. Please work with existing one.")

    def import_csv(self, fname: str, **kwargs):

        contents = pd.read_csv(fname, **kwargs)
        self.import_dataframe(contents)

    def import_dataframe(self, table: pd.DataFrame):

        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        logger.info(f"\n{table}")

        # Register aliases.
        logger.info("Registering simple aliases")
        for idx, row in table.iterrows():
            logger.debug(f"Row: {idx}")

            ds = get_value(row, "DS")
            name = get_value(row, "Variable")
            alias = get_value(row, "Alias")

            if not len(ds):
                logger.info("Data source is not specified")
                continue
            if not len(alias):
                logger.info("An alias is not specified")
                continue
            if not len(name):
                logger.info("Variable name is not specified")
                continue

            self.env.update_alias(ds, name, alias)

        logger.info("Registering composite/complex aliases")
        for idx, row in table.iterrows():
            logger.debug(f"Row: {idx}")

            ds = get_value(row, "DS")
            name = get_value(row, "Variable")
            alias = get_value(row, "Alias")
            
            if len(ds):
                logger.info("Data source is specified")
                continue
            if not len(alias):
                logger.info("An alias is not specified")
                continue
            if not len(name):
                logger.info("Variable name is not specified")
                continue

            self.env.update_alias(ds, name, alias)

        logger.info("Registering hash with signals")
        # For each row, create a signal if variable name is specified
        for idx, row in table.iterrows():
            logger.debug(f"Row: {idx}")

            ds = get_value(row, "DS")
            name = get_value(row, "Variable")

            # In order to access and share global aliases, load the signal into context.
            try:
                self.add_signal(ds, name)
            except (InvalidSignalName, InvalidExpression) as e:
                logger.warning(
                    f"ds: {ds}, name: {name} | Not a signal. {e}")
                continue

    def add_signal(self, data_source: str, name: str) -> typing.Tuple[str, Signal]:

        k, v = self.env.add_signal(data_source, name)

        parser = parsers.Parser()
        parser.set_expression(v.name)

        if not parser.is_valid:  # for single varname without '${', '}'
            v.expression = parser.marker_in + v.name + parser.marker_out
            parser.clear_expr()
            parser.set_expression(v.expression)
        else:
            v.expression = v.name

        # Initialize constituent variable names and their signals
        num_vars = len(parser.var_map.keys())
        if num_vars > 1:
            for var_name in parser.var_map.keys():
                v.var_names.add(var_name)
                if not self.env.is_alias(var_name):
                    self.add_signal(data_source, var_name)
        elif num_vars == 1:
            v.var_names.add(parser.var_map.popitem()[0])

        self._mod_time = time.time_ns()

        return k, v

    def build(self):

        if self._mod_time < self._build_time:
            return

        logger.debug("Building context map")

        for k, v in self.env.items():
            if not isinstance(v, Signal):
                continue

            logger.debug(f"k: {k} | v: {v}")
            v.debug_log()
            # now replace
            # 1. ascii varnames with the hash codes and
            # 2. aliases with their target hash codes
            for var_name in v.var_names:
                ds = v.data_source
                logger.debug(f"var_name: {var_name}")

                k, _ = self.env.get_signal(ds, var_name)
                logger.debug(f"k: {k} found!")

                v.expression = v.expression.replace(var_name, k)
                logger.debug(f"|==> replaced {var_name} with {k}")
                logger.debug(f"v.expression: {v.expression}")

        self._build_time = time.time_ns()

    def evaluate(self, expr: str, self_signal_hash: str = "", unbound_signal_handler: typing.Callable = None, **params):

        logger.info(
            f"Evaluating '{expr}', self_signal_hash='{self_signal_hash}'")

        local_env = dict(self._env)
        # Update value for the keyword "self", Ex: ${self}.time, ${self}.data
        if isinstance(self_signal_hash, str) and len(self_signal_hash):
            local_env.update({"self": self.env.get(self_signal_hash)})
        else:
            local_env.update({"self": None})

        # Check for undesired use of self in expression.
        if not isinstance(local_env.get("self"), Signal) and expr.count("self"):
            logger.warning(
                f"The expression:'{expr}' uses 'self' but self_signal_hash:'{self_signal_hash}' is invalid.")

        ds = params.get("DS") or params.get("ds") or params.get(
            "DataSource") or params.get("datasource") or ""
        logger.debug(f"DS='{ds}'")

        # Parse it
        p = parsers.Parser()
        p.supported_members.update(p.get_member_list(Signal))
        p.set_expression(expr)

        if not p.is_valid:
            raise InvalidExpression(
                f"Expression: {expr} is not a valid expression")

        for var_name in p.var_map.keys():
            
            logger.debug(f"var_name: {var_name}")
            sig = None

            if var_name == "self":
                sig = self.env[self_signal_hash]
                expr = expr.replace(var_name, self_signal_hash)
                logger.debug(f"|==> replaced {var_name} with {self_signal_hash}")
            else:
                try:
                    k, sig = self.env.get_signal(ds, var_name)
                    logger.debug(f"k: {k} found!")
                    sig.debug_log()
                    
                    matchString = p.marker_in + var_name + p.marker_out + '.time'
                    if expr.count(matchString):
                        p.has_time_units = True
                        replacement = f"{matchString}.astype('datetime64[{sig.time_unit}]')"
                        expr = expr.replace(matchString, replacement)

                    expr = expr.replace(var_name, k)
                    logger.debug(f"|==> replaced {var_name} with {k}")
                    logger.debug(f"expr: {expr}")

                except UnboundSignal as e:
                    if callable(unbound_signal_handler):
                        unbound_signal_handler(e.hashCode, ds, var_name)
                    continue
            
            logger.debug(f"Fetching resource.")
            logger.debug(f"params: {params}")

            dobj = self.data_access_callback(sig.data_source, sig.name, **params)
            Translator.new(sig.data_source).translate(dobj, sig)

        p.clear_expr()
        p.set_expression(expr)
        p.substitute_var(local_env)
        p.eval_expr()

        if isinstance(p.result, Signal):
            return p.result.data_primary
        else:
            if p.has_time_units:
                return p.result.astype('int64')
            else:
                return p.result
