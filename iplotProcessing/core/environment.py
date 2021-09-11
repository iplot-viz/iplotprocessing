import typing
from iplotProcessing.common.errors import UnboundSignal
from iplotProcessing.core.signal import Signal
from iplotProcessing.tools import hasher

from iplotLogging import setupLogger as sl

logger = sl.get_logger(__name__, level="INFO")


class Environment(dict):
    def add_signal(self, data_source: str, name: str) -> typing.Tuple[str, Signal]:
        hash_code = hasher.hash_tuple((data_source, name))
        try:
            return self.get_signal(data_source, name)
        except UnboundSignal:
            k, v = hash_code, Signal()

        v.data_source = data_source
        v.name = name
        logger.debug(f"Registered hash={hash_code} =>")
        logger.debug(f"sig={v}, ds={v.data_source}, name={v.name}")
        self.update({k: v})
        return k, v

    def is_alias(self, name: str):
        return isinstance(self.get(name), str)

    def get_hash(self, data_source: str, name: str) -> str:
        hash_code = hasher.hash_tuple((data_source, name))
        value = self.get(hash_code)

        if not isinstance(value, Signal):
            value = name
            while self.is_alias(value):
                value = self.get(name)
                hash_code = value

        return hash_code

    def get_signal(self, data_source: str, name: str) -> typing.Tuple[str, Signal]:
        hash_code = self.get_hash(data_source, name)
        value = self.get(hash_code)
        if not isinstance(value, Signal):
            raise UnboundSignal(hash_code, data_source, name)

        return hash_code, value

    def update_alias(self, data_source: str, name: str, alias: str):
        key = hasher.hash_tuple((data_source, name))
        logger.debug(f"Registered alias={alias} =>")
        logger.debug(f"ds={data_source}, name={name}, hash={key}")
        self.update({alias: key})
