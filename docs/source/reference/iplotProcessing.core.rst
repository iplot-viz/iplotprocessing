iplotProcessing.core module
===========================

.. _bufferobject:

BufferObject
-------------

A buffer object associates a physical unit attribute (eg: V, J, K, C, A, m, etc), a string
with a numpy.ndarray. It is derived from the ndarray class.

.. autoclass:: iplotProcessing.core.BufferObject
    :members:
    :undoc-members:


Signal
-------------

The signal class holds a combination of :ref:`bufferobject` (s)

When a signal is combined with other signals in mathematical expression,
the default mixing mode for time alignment is an intersection
of the individual time arrays.

The data values are then interpolated onto this new common time base.
The default kind of interpolation is linear.

Time
^^^^
    This is the time base for a signal, it could as well be another signal's data buffers.

Primary data
^^^^^^^^^^^^
    This is the data that is dependent on time. (could be independent)

Secondary data
^^^^^^^^^^^^^^
    This is the data that is dependent on time. (could be independent)

Examples
^^^^^^^^^^^^^^
1. For 1D signals:

    Ip = f(t)

    `data_primary` would be 'Ip'
    `time` would correspond to 't' variable

2. For 2D signals:

    Te = f(t, r)

    `data_primary` could be 'Te'
    `data_secondary` could be 'r'
    `time` would correspond to 't' variable.

.. note::

    `time` buffer could as well be replaced by `data_primary` from the first example.
    i.e, Te = f(Ip, r)

The name 'time' simply implies that it could be the basis for the data buffers.
It also helps in simpler naming of singal processing methods.

.. autoclass:: iplotProcessing.core.Signal
    :members:

Context
-------

.. autoclass:: iplotProcessing.core.Context
    :members:

Environment
-----------

.. autoclass:: iplotProcessing.core.Environment
    :members:

SignalDescription
-----------------

.. autoclass:: iplotProcessing.core.SignalDescription
    :members: