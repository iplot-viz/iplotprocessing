import typing
import numpy as np

def log(buffer: np.ndarray, c: typing.Any) -> np.ndarray:
    """Log of each buffer value with base 'c'

    Operation:
        log(buffer) / log(c)

    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with log of input values with base c
    """
    return np.log(buffer) / np.log(c)
