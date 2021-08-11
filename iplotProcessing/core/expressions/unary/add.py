import typing
import numpy as np

def add(buffer: np.ndarray, c: typing.Any) -> np.ndarray:
    """Add a constant to a buffer's values

    Operation:
        buffer + c

    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with c added to each value in buffer
    """
    return buffer + c
