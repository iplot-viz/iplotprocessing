import typing
import numpy as np

def power(buffer: np.ndarray, c: typing.Any) -> np.ndarray:
    """Raise each buffer value to power c

    Operation:
        buffer ** c

    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with each value raised to power c
    """
    return buffer ** c
