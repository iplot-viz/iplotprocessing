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
