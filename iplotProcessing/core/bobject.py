# Description: Combine unit attribute with numpy array
# Author: Jaswant Sai Panchumarti

import numpy as np


class BufferObject(np.ndarray):
    """A container of the data values
       and the corresponding unit attribute
    """

    def __new__(cls, input_arr=None, unit: str = '', shape=None, **kwargs):
        if shape is not None:
            obj = super().__new__(cls, shape, **kwargs)
        elif input_arr is not None:
            obj = np.asarray(input_arr).view(cls)
        else:
            obj = np.empty((0)).view(cls)

        obj.unit = unit
        return obj

    def __init__(self, input_arr=None, unit: str = '', shape=None, **kwargs) -> None:
        self.unit = unit

    def __array_finalize__(self, obj):
        if obj is None:
            return

        self.unit = getattr(obj, 'unit', None)

    # this method is called whenever you use a ufunc
    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """this implementation of __array_ufunc__ makes sure that all custom attributes are maintained when a ufunc operation is performed on our class."""

        args = ((i.view(np.ndarray) if isinstance(i, BufferObject) else i)
                for i in inputs)
        try:
            self_max_val = max(self)
        except ValueError:
            self_max_val = None

        outputs = kwargs.pop('out', None)
        if outputs:
            kwargs['out'] = tuple((o.view(np.ndarray) if isinstance(
                o, BufferObject) else o) for o in outputs)
        else:
            outputs = (None,) * ufunc.nout
        results = super().__array_ufunc__(ufunc, method, *args,
                                          **kwargs)  # pylint: disable=no-member
        if results is NotImplemented:
            return NotImplemented
        if method == 'at':
            return
        if ufunc.nout == 1:
            results = [results]

        # Cast a scalar or 0D array to a shape (1,) buffer object.
        for i in range(len(results)):
            if np.isscalar(results[i]) or (isinstance(results[i], BufferObject) and results[i].ndim == 0):
                results[i] = BufferObject([results[i]])

        results = tuple((self._copy_attrs_to(result) if output is None else output)
                        for result, output in zip(results, outputs))
        
        for result in results:
            # [IDV-280](https://jira.iter.org/browse/IDV-280). Clear unit attribute when processing occurs.
            if isinstance(result, BufferObject):
                result.unit = ''
            # if ufunc.__name__ in ['true_divide', 'floor_divide']:
            #     if isinstance(result, BufferObject) and self_max_val is not None:
            #         if result.unit.lower() in ['ns', 'nanoseconds']:
            #             if 1e9 - 1 <= self_max_val // max(result) <=  1e9:
            #                 result.unit = 'Seconds'
            #             elif 1e6 - 1 <= self_max_val // max(result) <=  1e6:
            #                 result.unit = 'ms'
            #             elif 1e3 - 1 <= self_max_val // max(result) <=  1e3:
            #                 result.unit = 'us'
            #         if result.unit.lower() in ['us', 'microseconds']:
            #             if 1e6 - 1 <= self_max_val // max(result) <= 1e6:
            #                 result.unit = 'Seconds'
            #             elif 1e3 - 1 <= self_max_val // max(result) <= 1e3:
            #                 result.unit = 'ms'
            #         if result.unit.lower() in ['ms', 'milliseconds']:
            #             if 1e3 - 1 <= self_max_val // max(result) <= 1e3:
            #                 result.unit = 'Seconds'
            # elif ufunc.__name__ in ['multiply']:
            #     if isinstance(result, BufferObject) and self_max_val is not None:
            #         if result.unit.lower() in ['us', 'microseconds']:
            #             if max(result) // self_max_val == 1e3:
            #                 result.unit = 'ns'
            #         if result.unit.lower() in ['ms', 'milliseconds']:
            #             if max(result) // self_max_val == 1e3:
            #                 result.unit = 'us'
            #             elif max(result) // self_max_val == 1e6:
            #                 result.unit = 'ns'
            #         if result.unit.lower() in ['s', 'seconds']:
            #             if max(result) // self_max_val == 1e3:
            #                 result.unit = 'ms'
            #             elif max(result) // self_max_val == 1e6:
            #                 result.unit = 'us'
            #             elif max(result) // self_max_val == 1e9:
            #                 result.unit = 'ns'
        return results[0] if len(results) == 1 else results

    def _copy_attrs_to(self, target):
        """copies all attributes of self to the target object. target must be a (subclass of) ndarray"""
        target = target.view(BufferObject)
        try:
            target.__dict__.update(self.__dict__)
        except AttributeError:
            pass
        return target
