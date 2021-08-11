import typing
import numpy as np

def divide_1(buffer: np.ndarray, c: typing.Any) -> np.ndarray:
    """Divide the buffer's values by a constant.
    
    Operation:
        buffer / c
    
    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with each input data's value divided by c
    """
    return buffer / c
