from iplotProcessing.tools import hasher

DEFAULT_PARAMS_ID = "a"

def getParamsId(params: dict):
    return DEFAULT_PARAMS_ID if not len(
        params) else hasher.hash_tuple(tuple(params.values()))