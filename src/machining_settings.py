class MachiningSettings:

    def __init__(self):
        self.target_position = {
            "x": None,
            "y": None,
            "z": None,
        }

        self.material = None
        self.process = None
        self.tool = None
        self.diameter = None
        self.depth = None
        self.rpm = None
        self.feed = None

    def get_status(self):
        position = self.target_position

        return (
            "Target Position\n"
            f"  x        : {position['x']} mm\n"
            f"  y        : {position['y']} mm\n"
            f"  z        : {position['z']} mm\n"
            "\n"
            "Machining\n"
            f"  Material : {self.material}\n"
            f"  Process  : {self.process}\n"
            f"  Tool     : {self.tool}\n"
            f"  Diameter : {self.diameter} mm\n"
            f"  Depth    : {self.depth} mm\n"
            f"  RPM      : {self.rpm} RPM\n"
            f"  Feed     : {self.feed} mm/rev"
        )