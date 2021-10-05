# Description: Combine unit attribute with numpy array
# Author: Jaswant Sai Panchumarti

import numpy as np


class BufferObject(np.ndarray):
    """A container of the data values and the corresponding unit attribute

    Scalars

        >>> from iplotProcessing.core import BufferObject
        >>> b0 = BufferObject(1, unit='A') # 0-D buffer
        >>> print(b0.shape)
        ()
        >>> print(b0.size)
        1
        >>> print(b0.unit)
        A
    
    Arrays

        >>> from iplotProcessing.core import BufferObject
        >>> b1 = BufferObject([1, 2], unit='ns') # 1-D buffer
        >>> print(b0.shape)
        (2,)
        >>> print(b1.size)
        2
        >>> print(b1.unit)
        ns
        >>> b2 = BufferObject([[1, 2], [3, 4], [5, 6]], unit='C') # 2-D buffer
        >>> print(b2.shape)
        (3, 2)
        >>> print(b2.size)
        6
        >>> print(b2.unit)
        C
    
    NumPy user functions
        
        >>> import numpy as np
        >>> from iplotProcessing.core import BufferObject
        >>> b = BufferObject(range(-5, 6), unit='ns')
        >>> np.sin(b)
        BufferObject([ 0.95892427,  0.7568025 , -0.14112001, -0.90929743,
                      -0.84147098,  0.        ,  0.84147098,  0.90929743,
                       0.14112001, -0.7568025 , -0.95892427])

        
        >>> import numpy as np
        >>> from iplotProcessing.core import BufferObject
        >>> b = BufferObject([0, 2, 3, 4, 5, 4, 2, 3], unit='ns')
        >>> np.histogram(b)
        (array([1, 0, 0, 0, 2, 0, 2, 0, 2, 1]), array([0. , 0.5, 1. , 1.5, 2. , 2.5, 3. , 3.5, 4. , 4.5, 5. ]))
        >>> np.sum(b)
        23
        >>> np.mean(b)
        2.875
        >>> np.median(b)
        3.0
        >>> np.fft.fft(b)
        array([23.        +0.j        , -7.12132034-0.29289322j,
                0.        +1.j        , -2.87867966+1.70710678j,
               -3.        +0.j        , -2.87867966-1.70710678j,
                0.        -1.j        , -7.12132034+0.29289322j])

    Advanced views
        
        >>> import numpy as np
        >>> from iplotProcessing.core import BufferObject
        >>> b = np.random.rand(10,2).view(BufferObject) # from a numpy array
        >>> print(b.shape)
        (10, 2)
        
        >>> import numpy as np
        >>> from iplotProcessing.core import BufferObject
        >>> np.ones((10,2)).view(BufferObject)
        BufferObject([[1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.],
                    [1., 1.]])

    Mathematical operations possible with NumPy.
        
        >>> import numpy as np
        >>> from iplotProcessing.core import BufferObject
        >>> b = np.ones((10)).view(BufferObject)
        >>> b + 2
        BufferObject([3. 3. 3. 3. 3. 3. 3. 3. 3. 3.])
        >>> b * 4
        BufferObject([4. 4. 4. 4. 4. 4. 4. 4. 4. 4.])
        
        >>> import numpy as np
        >>> from iplotProcessing.core import BufferObject
        >>> b = np.ones(shape=(3, 2)).view(BufferObject)
        >>> c = np.ones(shape=(2, 5)).view(BufferObject) * 2
        >>> d = np.matmul(b, c)
        >>> d
        BufferObject([[4., 4., 4., 4., 4.],
                    [4., 4., 4., 4., 4.],
                    [4., 4., 4., 4., 4.]])

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
