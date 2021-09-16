from collections import namedtuple
import time
import typing
import pandas as pd

from iplotProcessing.common.errors import InvalidExpression, InvalidSignalName, UnboundSignal
from iplotProcessing.common.table_parser import get_value, parse_timestamp, str_to_arr
from iplotProcessing.core.environment import Environment
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import parsers
from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="DEBUG")


SignalDescription = namedtuple('SignalDescription',
                               ['signals', 'col_num', 'row_num', 'stack_num', 'row_span',
                                   'col_span', 'pulsenb', 'start_ts', 'end_ts'],
                               defaults=[[], 0, 0, 0, 1, 1, None, None, None])


ContextT = typing.TypeVar('ContextT', bound="Context")

class Context:
    def __init__(self) -> None:

        self._env = Environment()

        self._build_time = time.time_ns()
        self._mod_time = time.time_ns()

    def reset(self) -> ContextT:
        self._env.clear()
        return self

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, val: dict):
        raise AttributeError(
            "Restricted access. Cannot assign an environment. Please work with existing one.")

    def import_csv(self, fname: str,
                   signal_class: type = Signal,
                   assort_signals: typing.Callable = None,
                   default_signal_params: dict = {},
                   **kwargs) -> ContextT:

        contents = pd.read_csv(fname, **kwargs)
        return self.import_dataframe(contents, signal_class,
                              assort_signals, **default_signal_params)

    def import_dataframe(self, table: pd.DataFrame,
                         signal_class: type = Signal,
                         assort_signals: typing.Callable = None,
                         default_dec_samples: int = 1000,
                         default_ts_start: int = -1,
                         default_ts_end: int = -1,
                         default_pulse_nb: typing.List[str] = []
                         ) -> ContextT:

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
                logger.debug("Data source is not specified")
                continue
            if not len(alias):
                logger.debug("An alias is not specified")
                continue
            if not len(name):
                logger.debug("Variable name is not specified")
                continue

            self.env.update_alias(ds, name, alias)

        logger.info("Registering composite/complex aliases")
        for idx, row in table.iterrows():
            logger.info(f"Row: {idx}")

            ds = get_value(row, "DS")
            name = get_value(row, "Variable")
            alias = get_value(row, "Alias")

            if len(ds):
                logger.debug("Data source is specified")
                continue
            if not len(alias):
                logger.debug("An alias is not specified")
                continue
            if not len(name):
                logger.debug("Variable name is not specified")
                continue

            self.env.update_alias(ds, name, alias)

        logger.info("Registering hash for signals")
        # For each row, try to create a signal
        for idx, row in table.iterrows():
            logger.debug(f"Row: {idx}")

            ds = get_value(row, "DS")
            name = get_value(row, "Variable")
            alias = get_value(row, "Alias")

            # type: typing.Unioin[str, None]
            sig_title = alias if len(alias) else None
            sig_title = None if isinstance(
                sig_title, str) and sig_title.isspace() else sig_title

            is_envelope = True
            if get_value(row, "Envelope") == '0':
                is_envelope = False
            elif get_value(row, "Envelope") == '':
                is_envelope = False
            elif get_value(row, "Envelope").isspace():
                is_envelope = False

            sig_dec_samples = get_value(
                row, "Samples", int) or default_dec_samples
            sig_pulse_nb = default_pulse_nb if isinstance(default_pulse_nb, list) and len(
                default_pulse_nb) > 0 else None
            sig_ts_start = default_ts_start if default_ts_start >= 0 else None
            sig_ts_end = default_ts_end if default_ts_end >= 0 else None
            sig_x_expr = get_value(row, "x") or "${self}.time"
            sig_y_expr = get_value(row, "y") or "${self}.data"
            sig_z_expr = get_value(row, "z") or "${self}.data_secondary"

            # deal with per-signal overrides.
            pulse_nb_override = get_value(row, "PulseNumber", str_to_arr)
            ts_start_override = get_value(row, "StartTime", parse_timestamp)
            ts_end_override = get_value(row, "EndTime", parse_timestamp)

            # If any of the override values is set we discard defaults
            if ts_start_override is not None or ts_end_override is not None or pulse_nb_override is not None:
                sig_pulse_nb = pulse_nb_override
                sig_ts_start = ts_start_override
                sig_ts_end = ts_end_override

            params = dict(name=name,
                          data_source=ds,
                          title=sig_title,
                          envelope=is_envelope,
                          dec_samples=sig_dec_samples,
                          ts_start=sig_ts_start,
                          ts_end=sig_ts_end,
                          x_expr=sig_x_expr,
                          y_expr=sig_y_expr,
                          z_expr=sig_z_expr,
                          )

            # In order to access and share global aliases, load the signal into context.
            signals = []
            try:
                if isinstance(sig_pulse_nb, list) and len(sig_pulse_nb) > 0:
                    for e in sig_pulse_nb:
                        params.update({"pulse_nb": e, "ts_relative": True})
                        _, signal = self.add_signal(
                            ds, name, signal_class, signal_params=params)
                        signals.append(signal)
                else:
                    _, signal = self.add_signal(
                        ds, name, signal_class, signal_params=params)
                    signals.append(signal)
            except (InvalidSignalName, InvalidExpression) as e:
                logger.warning(
                    f"ds: {ds}, name: {name} | Not a signal. {e}")
                if assort_signals:
                    assort_signals(SignalDescription())
                continue

            stack_val = str(get_value(row, "Stack")).split('.')
            col_num = int(stack_val[0]) if len(
                stack_val) > 0 and stack_val[0] else 0
            row_num = int(stack_val[1]) if len(
                stack_val) > 1 and stack_val[1] else 0
            stack_num = int(stack_val[2]) if len(
                stack_val) > 2 and stack_val[2] else 1

            row_span = get_value(row, "Row span", int) or 1
            col_span = get_value(row, "Col span", int) or 1

            payload = SignalDescription(
                signals, col_num, row_num, stack_num, row_span, col_span, sig_pulse_nb, sig_ts_start, sig_ts_end)

            if assort_signals:
                assort_signals(payload)

        return self

    def add_signal(self, data_source: str, name: str, signal_class: type = Signal, signal_params: dict = {}) -> typing.List[typing.Tuple[str, Signal]]:

        # build up an expression to determine each constituent variable name or alias.
        parser = parsers.Parser()
        parser.set_expression(name)

        validated_expression = ""
        if parser.is_valid:
            validated_expression = name
        else:
            validated_expression = parser.marker_in + name + parser.marker_out
            parser.set_expression(validated_expression)
            if not parser.is_valid:
                raise InvalidExpression

        # Register the data_source, name.
        k, v = self.env.add_signal(
            data_source, name, signal_class, signal_params)
        v.set_expression(validated_expression)
        v.var_names.clear()

        # Store constituent variable names
        for var_name in parser.var_map.keys():
            v.var_names.append(var_name)

        # Create signals for constituent var names
        for var_name in v.var_names:

            if self.env.is_alias(var_name):
                continue

            signal_params.update({"name": var_name})
            
            if v.is_composite:
                self.add_signal(data_source, var_name,
                            signal_class, signal_params)
            elif v.is_expression: # this clause covers a very rare corner case. ex: name = "${CWS-SCSU-HR00:ML0004-LT-XI}"
                _, sig = self.env.add_signal(data_source, var_name,
                            signal_class, signal_params)
                sig.set_expression(parser.marker_in + var_name + parser.marker_out)
                sig.var_names.append(var_name)
                break
        
        self._mod_time = time.time_ns()
        return k, v

    def modify(self) -> ContextT:
        self._mod_time = self._build_time
        return self

    def build(self) -> ContextT:

        if self._mod_time < self._build_time:
            return self

        logger.info("Building context map")

        for k, v in self.env.items():
            if not isinstance(v, Signal):
                continue

            logger.debug(f"k: {k} | v: {v}")
            # now replace
            # 1. ascii varnames with the hash codes and
            # 2. aliases with their target hash codes
            for var_name in v.var_names:
                ds = v.data_source
                logger.debug(f"var_name: {var_name}")

                k, _ = self.env.get_signal(ds, var_name)
                logger.debug(f"k: {k} found!")

                v.set_expression(v.expression.replace(var_name, k))
                logger.debug(f"|==> replaced {var_name} with {k}")
                logger.debug(f"v.expression: {v.expression}")

        return self.modify()

    def evaluate_signal(self, sig: Signal, unbound_signal_handler: typing.Callable, fetch_on_demand: bool = True, **params) -> ContextT:
        logger.info(f"Evaluating signal: {sig}")
        k = self.env.get_hash(sig.data_source, sig.name)

        if k not in self.env.keys():
            unbound_signal_handler(k, sig)
            return self

        # Backup the existing parameters and use the parameters specified in arguments.
        params_stack = dict()
        for k, v in params.items():
            if hasattr(sig, k):
                params_stack.update({k: v})
                setattr(sig, k, v)

        if sig.is_composite or sig.is_expression:
            for var_name in sig.var_names:
                try:
                    hc, v = self.env.get_signal(sig.data_source, var_name)
                except UnboundSignal:
                    unbound_signal_handler(hc, sig)
                    continue
                self.evaluate_signal(v, fetch_on_demand, unbound_signal_handler, **params)
        else:
            if hasattr(sig, 'fetch_data') and fetch_on_demand:
                sig.fetch_data()
        
        # restore the original parameters
        for k, v in params_stack.items():
            setattr(sig, k, v)

        new_sig = parsers.Parser()          \
            .set_expression(sig.expression) \
            .substitute_var(self.env)       \
            .eval_expr()                    \
            .result
        
        if hasattr(new_sig, "copy_buffers_to"):
            new_sig.copy_buffers_to(sig)
        
        return self

    def evaluate_expr(self, expr: str, self_signal_hash: str = "", fetch_on_demand=True, unbound_signal_handler: typing.Callable = None, **params):

        logger.info(
            f"Evaluating '{expr}', self_signal_hash='{self_signal_hash}', fetch_on_demand={fetch_on_demand}")

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
            "DataSource") or params.get("data_source") or ""
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
                hash_code = self_signal_hash
                sig = self.env[self_signal_hash]
            else:
                try:
                    hash_code, sig = self.env.get_signal(ds, var_name)
                    logger.debug(f"k: {hash_code} found!")
                    sig.debug_log()

                except UnboundSignal as e:
                    if callable(unbound_signal_handler):
                        unbound_signal_handler(e.hashCode, ds, var_name)
                    continue

            if hasattr(sig, "fetch_data") and fetch_on_demand:
                sig.fetch_data()

            match = p.marker_in + var_name + p.marker_out + '.time'
            if expr.count(match) and p.has_time_units:
                if sig.time_unit == "nanoseconds":
                    sig.time_unit = 'ns'
                replacement = f"{match}.astype('datetime64[{sig.time_unit}]')"
                expr = expr.replace(match, replacement)
                logger.debug(f"|==> replaced {match} with {replacement}")
                logger.debug(f"expr: {expr}")

            expr = expr.replace(var_name, hash_code)
            logger.debug(f"|==> replaced {var_name} with {hash_code}")
            logger.debug(f"expr: {expr}")

        p.clear_expr()
        p.set_expression(expr)
        p.substitute_var(local_env)
        p.eval_expr()

        if isinstance(p.result, Signal):
            return p.result
        else:
            if p.has_time_units:
                return p.result.astype('int64')
            else:
                return p.result
