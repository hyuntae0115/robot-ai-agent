class MachiningSettings:
    def __init__(self):
        self.target_position = {
            "x": None,
            "y": None,
            "z": None,
        }

        self.material = None
        self.rpm = 0
        self.depth = 0
        self.tool = None
        self.tool_diameter = None

    def get_status(self):
        position = self.target_position

        return (
            f"Target position\n"
            f"  x      : {position['x']} mm\n"
            f"  y      : {position['y']} mm\n"
            f"  z      : {position['z']} mm\n"

            f"Machining\n"
            f"  Material : {self.material}\n"
            f"  RPM      : {self.rpm}\n"
            f"  Depth    : {self.depth} mm\n"
            f"  Tool     : {self.tool}\n"
            f"  Diameter : {self.tool_diameter} mm"
        )