# Description: Combine unit attribute with numpy array
# Author: Jaswant Sai Panchumarti

import numpy as np

class BufferObject(np.ndarray):
    """A container of the data values
       and the corresponding unit attribute
    """

    def __new__(cls, input_arr=None, unit: str='', shape=None, **kwargs):
        if shape is not None:
            obj = super().__new__(cls, shape, **kwargs)
        elif input_arr is not None:
            obj = np.asarray(input_arr).view(cls)
        else:
            obj = np.empty((0)).view(cls)

        obj.unit = unit
        return obj

    def __init__(self, input_arr=None, unit: str='', shape=None, **kwargs) -> None:
        self.unit = unit

    def __array_finalize__(self, obj):
        if obj is None:
            return
        
        self.unit = getattr(obj, 'unit', None)
    
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):  # this method is called whenever you use a ufunc
            """this implementation of __array_ufunc__ makes sure that all custom attributes are maintained when a ufunc operation is performed on our class."""

            args = ((i.view(np.ndarray) if isinstance(i, BufferObject) else i) for i in inputs)
            outputs = kwargs.pop('out', None)
            if outputs:
                kwargs['out'] = tuple((o.view(np.ndarray) if isinstance(o, BufferObject) else o) for o in outputs)
            else:
                outputs = (None,) * ufunc.nout
            results = super().__array_ufunc__(ufunc, method, *args, **kwargs)  # pylint: disable=no-member
            if results is NotImplemented:
                return NotImplemented
            if method == 'at':
                return
            if ufunc.nout == 1:
                results = (results,)
            results = tuple((self._copy_attrs_to(result) if output is None else output)
                            for result, output in zip(results, outputs))
            return results[0] if len(results) == 1 else results

    def _copy_attrs_to(self, target):
        """copies all attributes of self to the target object. target must be a (subclass of) ndarray"""
        target = target.view(BufferObject)
        try:
            target.__dict__.update(self.__dict__)
        except AttributeError:
            pass
        return target