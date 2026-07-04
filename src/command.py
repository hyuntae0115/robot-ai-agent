class Command:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __str__(self):
        return f"Command(name={self.name}, args={self.args})"