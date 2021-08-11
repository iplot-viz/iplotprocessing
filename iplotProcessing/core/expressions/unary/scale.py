import typing
import numpy as np

def power(buffer: np.ndarray, c1: typing.Any, c2: typing.Any=0) -> np.ndarray:
    """Scale buffer by c1 and add c2

    Operation:
        (buffer * c1) + c2

    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with each value scaled by c1 and incremented by c2
    """
    return (buffer * c1) + c2
