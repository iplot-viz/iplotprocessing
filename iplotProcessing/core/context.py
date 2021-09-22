from collections import namedtuple
import typing
import pandas as pd

from iplotProcessing.common.errors import InvalidExpression, UnboundSignal
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

    def parse_series(self,
                     inp: pd.Series,
                     default_dec_samples: int = 1000,
                     default_ts_start: int = -1,
                     default_ts_end: int = -1,
                     default_pulse_nb: typing.List[str] = []
                     ) -> typing.Iterator[pd.Series]:

        column_names = list(Environment.get_column_names())

        ds = get_value(inp, "DS")
        name = get_value(inp, "Variable")
        alias = get_value(inp, "Alias")

        is_envelope = True
        if get_value(inp, "Envelope") == '0':
            is_envelope = False
        elif get_value(inp, "Envelope") == '':
            is_envelope = False
        elif get_value(inp, "Envelope").isspace():
            is_envelope = False

        sig_dec_samples = get_value(
            inp, "Samples", int) or default_dec_samples
        sig_pulse_nb = default_pulse_nb if isinstance(default_pulse_nb, list) and len(
            default_pulse_nb) > 0 else None
        sig_ts_start = default_ts_start if default_ts_start >= 0 else None
        sig_ts_end = default_ts_end if default_ts_end >= 0 else None
        sig_x_expr = get_value(inp, "x") or "${self}.time"
        sig_y_expr = get_value(inp, "y") or "${self}.data"
        sig_z_expr = get_value(inp, "z") or "${self}.data_secondary"
        sig_plot_type = get_value(inp, "Plot type") or "PlotXY"

        # deal with per-signal overrides.
        pulse_nb_override = get_value(inp, "PulseNumber", str_to_arr)
        ts_start_override = get_value(inp, "StartTime", parse_timestamp)
        ts_end_override = get_value(inp, "EndTime", parse_timestamp)

        # If any of the override values is set we discard defaults
        if ts_start_override is not None or ts_end_override is not None or pulse_nb_override is not None:
            sig_pulse_nb = pulse_nb_override
            sig_ts_start = ts_start_override
            sig_ts_end = ts_end_override

        sig_stack_val = str(get_value(inp, "Stack"))
        sig_row_span = get_value(inp, "Row span", int) or 1
        sig_col_span = get_value(inp, "Col span", int) or 1

        if isinstance(sig_pulse_nb, list) and len(sig_pulse_nb) > 0:
            for e in sig_pulse_nb:
                data = [ds, name, alias, sig_stack_val, sig_row_span, sig_col_span, is_envelope, sig_dec_samples, e,
                        sig_ts_start, sig_ts_end, sig_x_expr, sig_y_expr, sig_z_expr, sig_plot_type]
                yield pd.Series(data, index=column_names)
        else:
            data = [name, ds, alias, sig_stack_val, sig_row_span, sig_col_span, is_envelope, sig_dec_samples, None,
                    sig_ts_start, sig_ts_end, sig_x_expr, sig_y_expr, sig_z_expr, sig_plot_type]
            yield pd.Series(data, index=column_names)

    def import_dataframe(self, table: pd.DataFrame,
                         signal_class: type = Signal,
                         assort_signals: typing.Callable = None,
                         default_dec_samples: int = 1000,
                         default_ts_start: int = -1,
                         default_ts_end: int = -1,
                         default_pulse_nb: typing.List[str] = []
                         ) -> ContextT:
        
        for col_name in Environment.get_column_names():
            if col_name not in table.columns:
                table[col_name] = [''] * table.count(1).index.size

        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)
        logger.info(f"\n{table}")

        default_params = dict(default_dec_samples=default_dec_samples,
                              default_ts_start=default_ts_start,
                              default_ts_end=default_ts_end,
                              default_pulse_nb=default_pulse_nb)
        logger.info("Registering aliases")
        for idx, row in table.iterrows():
            logger.debug(f"Row: {idx}")

            for parsed_row in self.parse_series(row, **default_params):
                signal_params = Environment.construct_params_from_series(
                    parsed_row)
                uid = Environment.construct_uid(**signal_params)
                alias = parsed_row['Alias']
                self.env.add_alias(alias, uid)

        logger.info("Registering signals")
        for idx, row in table.iterrows():
            logger.debug(f"Row: {idx}")
            signals = []
            signal_params = dict()

            for parsed_row in self.parse_series(row, **default_params):
                signal_params.update(Environment.construct_params_from_series(
                    parsed_row))

                if signal_params.get('pulse_nb') is not None:
                    signal_params.update({'ts_relative': True})
                    _, signal = self.env.add_signal(
                        signal_class, **signal_params)
                    signals.append(signal)
                else:
                    _, signal = self.env.add_signal(
                        signal_class, **signal_params)
                    signals.append(signal)

            if not len(signal_params):
                continue

            breakpoint()
        
            stack_val = signal_params.get('stack_val').split('.')
            col_num = int(stack_val[0]) if len(
                stack_val) > 0 and stack_val[0] else 0
            row_num = int(stack_val[1]) if len(
                stack_val) > 1 and stack_val[1] else 0
            stack_num = int(stack_val[2]) if len(
                stack_val) > 2 and stack_val[2] else 1

            payload = SignalDescription(signals, col_num, row_num, stack_num, signal_params['row_span'],
                                        signal_params['col_span'], signal_params['pulse_nb'], signal_params['ts_start'], signal_params['ts_end'])

            if assort_signals:
                assort_signals(payload)

        return self

    def build(self) -> ContextT:

        logger.info("Building context map")

        for k, v in self.env.items():
            if not isinstance(v, Signal):
                continue

            logger.debug(f"k: {k} | v: {v}")
            signal_params = Environment.construct_params_from_signal(v)
            logger.debug(f"{signal_params}")
            name_key = Environment.header.get('Variable').get('code_name')

            # now replace
            # 1. ascii varnames with the hash codes and
            # 2. aliases with their target hash codes
            for var_name in v.var_names:
                logger.debug(f"var_name: {var_name}")

                signal_params.update({name_key: var_name})
                k, _ = self.env.get_signal(**signal_params)
                logger.debug(f"k: {k} found!")

                v.set_expression(v.expression.replace(var_name, k))
                logger.debug(f"|==> replaced {var_name} with {k}")
                logger.debug(f"v.expression: {v.expression}")

        return self

    def evaluate_signal(self, sig: Signal, unbound_signal_handler: typing.Callable, fetch_on_demand: bool = True, **params) -> ContextT:
        logger.info(f"Evaluating signal: {sig}")
        uid = Environment.construct_uid_from_signal(sig)

        if uid not in self.env.keys():
            raise UnboundSignal(uid)

        # Backup the signal's values of specified parameters and use the values from the params argument.
        params_stack = dict()
        for k, v in params.items():
            if hasattr(sig, k):
                params_stack.update({k: v})
                setattr(sig, k, v)

        signal_params = Environment.construct_params_from_signal(sig)
        if sig.is_composite or sig.is_expression:
            name_key = Environment.header.get('Variable').get('code_name')
            for var_name in sig.var_names:
                signal_params.update({name_key: var_name})
                try:
                    _, v = self.env.get_signal(**signal_params)
                except UnboundSignal as e:
                    logger.exception(e)
                    if callable(unbound_signal_handler):
                        unbound_signal_handler(e)
                        continue
                self.evaluate_signal(
                    v, unbound_signal_handler, fetch_on_demand, **params)
        else:
            if hasattr(sig, 'fetch_data') and fetch_on_demand:
                sig.fetch_data()

        # restore the original parameters
        for k, v in params_stack.items():
            setattr(sig, k, v)
        try:
            new_sig = parsers.Parser()          \
                .set_expression(sig.expression) \
                .substitute_var(self.env)       \
                .eval_expr()                    \
                .result

            if hasattr(new_sig, "copy_buffers_to"):
                new_sig.copy_buffers_to(sig)
            
        except InvalidExpression as e:
            logger.exception(e)

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
                uid = self_signal_hash
                sig = self.env[self_signal_hash]
            else:
                try:
                    value = var_name
                    while self.env.is_alias(value):
                        value = self.env.get(value)
                    uid = value

                    sig = self.env.get(uid)
                    if not isinstance(sig, Signal):
                        raise UnboundSignal(uid)

                    logger.debug(f"k: {uid} found!")
                    sig.debug_log()

                except UnboundSignal as e:
                    logger.exception(e)
                    if callable(unbound_signal_handler):
                        unbound_signal_handler(e)
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

            expr = expr.replace(var_name, uid)
            logger.debug(f"|==> replaced {var_name} with {uid}")
            logger.debug(f"expr: {expr}")

        p.clear_expr()
        p.set_expression(expr)
        p.substitute_var(local_env)

        try:
            p.eval_expr()
        except InvalidExpression as e:
            logger.exception(e)
            return None

        if isinstance(p.result, Signal):
            return p.result
        else:
            if p.has_time_units:
                return p.result.astype('int64')
            else:
                return p.result
