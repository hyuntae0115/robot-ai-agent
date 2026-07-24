class CommandContext:
    def __init__(self):
        self.is_active = False

        self.pending_target = {
            "x": None,
            "y": None,
            "z": None
        }

        self.pending_machine = {
            "process": None,
            "material": None,
            "rpm": None,
            "depth": None,
            "tool": None,
            "diameter": None
        }

    def clear(self):
        self.is_active = False

        self.pending_target = {
            "x": None,
            "y": None,
            "z": None
        }

        self.pending_machine = {
            "process": None,
            "material": None,
            "rpm": None,
            "depth": None,
            "tool": None,
            "diameter": None
        }