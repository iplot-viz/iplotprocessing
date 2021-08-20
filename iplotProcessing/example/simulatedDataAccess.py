import numpy as np
import time

def getData(varname: str):
    seed = hash(varname) + time.time_ns()
    return np.arange(seed, seed + 16)