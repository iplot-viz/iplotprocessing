# Description: Used by the library to indicate invalid attributes were specified
# Author: Jaswant Sai Panchumarti

class UnboundSignal(Exception):
    def __init__(self, uid: str, **params):
        self.uid = uid
        self.params = params

    def __str__(self):
        return f"""UID: {self.uid},
        params: {self.params}, 
        is not defined in environment"""

class InvalidSignalName(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidExpression(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
