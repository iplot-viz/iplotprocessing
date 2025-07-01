# Copyright (c) 2020-2025 ITER Organization,
#               CS 90046
#               13067 St Paul Lez Durance Cedex
#               France
# Author IO
#
# This file is part of iplotprocessing module.
# iplotprocessing python module is free software: you can redistribute it and/or modify it under
# the terms of the MIT license.
#
# This file is part of ITER CODAC software.
# For the terms and conditions of redistribution or use of this software
# refer to the file LICENSE located in the top level directory
# of the distribution package
#


# Description: Used by the library to indicate invalid attributes were specified
# Author: Jaswant Sai Panchumarti

class InvalidExpression(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidNDims(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidVariable(Exception):
    def __init__(self, _var_map: dict, _locals: dict, *args: object) -> None:
        super().__init__(*args)
        self.invalid_keys = set()
        for k in _var_map.keys():
            if k not in _locals.keys():
                self.invalid_keys.add(k)

    def __str__(self) -> str:
        return f"""Following keys are undefined {self.invalid_keys}"""
