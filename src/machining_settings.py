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

    @staticmethod
    def format_position_m(value):
        if value is None:
            return "None"

        return f"{value / 1000.0:.3f}"

    def get_status(self):
        position = self.target_position

        return (
            "Target Position\n"
            f"  x        : {self.format_position_m(position['x'])} m\n"
            f"  y        : {self.format_position_m(position['y'])} m\n"
            f"  z        : {self.format_position_m(position['z'])} m\n"
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