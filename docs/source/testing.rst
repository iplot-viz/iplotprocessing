
.. _testing:

Testing
-------

Run the unit tests to verify your installation is stable.

.. code-block:: bash

    $ pytest iplotProcessing

You should see the following output.

.. code-block:: bash

    ==================================================================== test session starts =====================================================================
    platform linux -- Python 3.8.6, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
    rootdir: /home/ITER/panchuj/Downloads/work/iterplotlib/iplotprocessing
    collected 24 items                                                                                                                                           

    iplotProcessing/tests/test_01_expression_parsing.py .....                                                                                              [ 20%]
    iplotProcessing/tests/test_02_dobject_0d_buffer.py ..                                                                                                  [ 29%]
    iplotProcessing/tests/test_03_dobject_1d_buffer.py .                                                                                                   [ 33%]
    iplotProcessing/tests/test_04_dobject_2d_buffer.py .                                                                                                   [ 37%]
    iplotProcessing/tests/test_05_signal_time.py .                                                                                                         [ 41%]
    iplotProcessing/tests/test_06_signal_primary_indirect.py .                                                                                             [ 45%]
    iplotProcessing/tests/test_07_signal_primary_direct.py .                                                                                               [ 50%]
    iplotProcessing/tests/test_08_signal_primary_mixed1.py .                                                                                               [ 54%]
    iplotProcessing/tests/test_09_signal_primary_mixed2.py .                                                                                               [ 58%]
    iplotProcessing/tests/test_10_signal_secondary.py .                                                                                                    [ 62%]
    iplotProcessing/tests/test_11_context_attribute_protection.py .                                                                                        [ 66%]
    iplotProcessing/tests/test_12_env_aliasing.py .                                                                                                        [ 70%]
    iplotProcessing/tests/test_13_context_refresh.py .                                                                                                     [ 75%]
    iplotProcessing/tests/test_14_time_resolution.py ..                                                                                                    [ 83%]
    iplotProcessing/tests/test_15_time_mixin_intersection.py ..                                                                                            [ 91%]
    iplotProcessing/tests/test_16_time_mixin_union.py ..                                                                                                   [100%]

    ===================================================================== 24 passed in 3.74s =====================================================================
