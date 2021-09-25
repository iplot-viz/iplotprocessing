# Description: Manage aliases and signals with a Universal Identifier
#              constructed from important fields (DataSource, VarName, Time range, Pulse number, etc)
# Author: Jaswant Sai Panchumarti

import importlib
import json
import os
import pandas as pd
import typing

from iplotProcessing.common.errors import InvalidExpression, UnboundSignal
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher, parsers

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="DEBUG")

DEFAULT_BLUEPRINT_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "blueprint.json")


class Environment(dict):
    blueprint: dict = {}

    @staticmethod
    def get_column_names() -> typing.Iterator[str]:
        for k, v in Environment.blueprint.items():
            if not v.get('computed'):
                yield Environment.get_column_name(k)

    @staticmethod
    def get_column_name(key: str) -> str:
        return Environment.blueprint.get(key).get('label') or key

    @staticmethod
    def get_keys_with_override() -> typing.Iterator[str]:
        for k, v in Environment.blueprint.items():
            if v.get('override'):
                yield k

    @staticmethod
    def construct_uid(**signal_params) -> str:
        params = []
        for v in Environment.blueprint.values():
            if not v.get('no_hash'):
                k = signal_params.get(v.get('code_name'))
                val = signal_params.get(k)
                params.append((k, val))
        return hasher.hash_tuple(tuple(params))

    @staticmethod
    def construct_signal(signal_class: type = Signal, **signal_params) -> Signal:
        for v in Environment.blueprint.values():
            if v.get('no_construct'):
                try:
                    signal_params.pop(v.get('code_name'))
                except KeyError:
                    continue
        return signal_class(**signal_params)

    @staticmethod
    def construct_uid_from_signal(sig: Signal) -> str:
        return Environment.construct_uid(**Environment.construct_params_from_signal(sig))

    @staticmethod
    def construct_params_from_signal(sig: Signal) -> dict:
        params = {}
        for v in Environment.blueprint.values():
            cname = v.get('code_name')
            try:
                value = getattr(sig, cname)
                params.update({cname: value})
            except AttributeError:
                logger.debug(f"Ignoring {v}")
                continue
        return params

    @staticmethod
    def construct_params_from_series(row: pd.Series) -> dict:
        params = {}
        for k, v in Environment.blueprint.items():
            column_name = v.get('label') or k
            code_name = v.get('code_name')
            try:
                params.update({code_name: row[column_name]})
            except KeyError:
                logger.debug(f"Ignoring {k}, {v}")
                continue
        return params

    @staticmethod
    def adjust_dataframe(df: pd.DataFrame):
        for col_name in Environment.get_column_names():
            if col_name not in df.columns:
                df[col_name] = [''] * df.count(1).index.size

    def __init__(self, *args, blueprint_file: os.PathLike = DEFAULT_BLUEPRINT_FILE, **kwargs):
        super().__init__(*args, **kwargs)

        logger.debug(f"Loading table description {blueprint_file}")
        with open(blueprint_file) as f:
            Environment.blueprint = json.load(f)
            for k, v in Environment.blueprint.items():
                if v.get('type'):
                    type_name = v.get('type')
                    parts = type_name.split('.')
                    try:
                        type_func = getattr(importlib.import_module(
                            '.'.join(parts[:-1])), parts[-1])
                    except ValueError:
                        type_func = getattr(
                            importlib.import_module("builtins"), type_name)
                    assert callable(type_func)
                    v.update({'type': type_func})
                    logger.debug(f"Updated {k}.type = {type_func}")

        logger.debug(f"Loaded table description {Environment.blueprint}")
        self._table = list()

    def validate(self, mask: str, **signal_params):
        for v in Environment.blueprint.values():
            code_name = v.get('code_name')
            if v.get(mask):
                continue
            else:
                assert code_name in signal_params.keys()

    def export_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self._table)

    def add_signal(self, signal_class: type = Signal, **signal_params) -> typing.List[typing.Tuple[str, Signal]]:

        logger.debug(f"signal_class={signal_class}")
        logger.debug(f"signal_params={signal_params}")

        self.validate(mask='no_construct', **signal_params)

        name = signal_params.get('name')
        parser = parsers.Parser().set_expression(name)

        validated_expression = ""
        if parser.is_valid:
            validated_expression = name
        else:
            validated_expression = parser.marker_in + name + parser.marker_out
            parser.set_expression(validated_expression)
            if not parser.is_valid:
                raise InvalidExpression
            if name == '':
                parser.clear_expr()
                validated_expression = ''

        # Register the signal into environment
        try:
            return self.get_signal(**signal_params)
        except UnboundSignal:
            uid, sig = self._finalize_signal(signal_class, **signal_params)
            sig.set_expression(validated_expression)

            # Store constituent variable names
            sig.var_names.clear()
            sig.var_names.extend(parser.var_map.keys())

            # Create signals for constituent var names
            for var_name in sig.var_names:

                if self.is_alias(var_name):
                    continue

                signal_params.update({"name": var_name})

                if sig.is_composite:
                    self.add_signal(signal_class, **signal_params)
                # this clause covers a very rare corner case. ex: name = "${CWS-SCSU-HR00:ML0004-LT-XI}"
                elif sig.is_expression:
                    _, v = self._finalize_signal(signal_class, **signal_params)
                    v.set_expression(parser.marker_in +
                                     var_name + parser.marker_out)
                    v.var_names.append(var_name)
                    break

            return uid, sig

    def _finalize_signal(self, signal_class: type = Signal, **signal_params) -> typing.Tuple[str, Signal]:

        row_contents = {k: signal_params.get(
            v.get('code_name')) for k, v in Environment.blueprint.items()}

        uid = self.construct_uid(**signal_params)
        sig = self.construct_signal(signal_class, **signal_params)
        self.update({uid: sig})

        logger.debug(f"Registered hash={uid} =>")
        logger.debug(f"sig={sig}")

        row_contents.update({'UIDs': uid})
        self._table.append(row_contents)

        return uid, sig

    def is_alias(self, name: str):
        return isinstance(self.get(name), str)

    def get_uid(self, **signal_params) -> str:
        self.validate(mask='no_construct', **signal_params)
        uid = self.construct_uid(**signal_params)
        value = self.get(uid)
        name = signal_params.get(
            Environment.blueprint['Variable'].get('code_name'))

        if not isinstance(value, Signal):
            value = name
            while self.is_alias(value):
                value = self.get(value)
                uid = value

        return uid

    def get_signal(self, **signal_params) -> typing.Tuple[str, Signal]:
        uid = self.get_uid(**signal_params)
        value = self.get(uid)
        if not isinstance(value, Signal):
            raise UnboundSignal(uid, **signal_params)

        return uid, value

    def add_alias(self, alias: str, uid: str):
        if alias:
            if alias not in self.keys():
                logger.debug(f"Registered alias={alias} => uid={uid}")
                self.update({alias: uid})
            else:
                logger.warning(
                    f"Redfined {alias}. Loss of existing {alias} => {self.get(alias)}")
