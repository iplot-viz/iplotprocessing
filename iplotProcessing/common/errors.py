class UnboundSignal(Exception):
    def __init__(self, hc: str, ds: str, name: str):
        self.hash_code = hc
        self.ds = ds
        self.name = name

    def __str__(self):
        return f"""HashCode: {self.hash_code},
        DataSource: {self.ds}, 
        Name: {self.name}, 
        is not defined in environment"""

class InvalidSignalName(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidExpression(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
