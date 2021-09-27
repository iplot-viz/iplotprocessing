import typing
import numpy as np

def multiply(buffer: np.ndarray, c: typing.Any) -> np.ndarray:
    """Multiply a constant to a buffer's values

    Operation:
        buffer * c

    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with c multiplied to each value in buffer
    """
    return buffer * c
