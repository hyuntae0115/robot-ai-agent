class Command:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.args = kwargs