import typing
import numpy as np

def divide_2(buffer: np.ndarray, c: typing.Any) -> np.ndarray:
    """Divide the constant by each of the buffer's values.
    
    Operation:
        c / buffer

    Args:
        buffer (np.ndarray): input data
        c (typing.Any): a constant

    Returns:
        np.ndarray: new array with c divided by each input data's value
    """
    return c / buffer
