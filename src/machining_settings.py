class Machining_Settings:
    def __init__(self):
        self.target_pose = {
            "x": None,
            "y": None,
            "z": None,
            "roll": None,
            "pitch": None,
            "yaw": None
        }

        self.material = None
        self.rpm = 0
        self.depth = 0
        self.tool = None

    def get_status(self):
        pose = self.target_pose

        return (
            f"Target Pose\n"
            f"  x      : {pose['x']} mm\n"
            f"  y      : {pose['y']} mm\n"
            f"  z      : {pose['z']} mm\n"
            f"  roll   : {pose['roll']}°\n"
            f"  pitch  : {pose['pitch']}°\n"
            f"  yaw    : {pose['yaw']}°\n\n"

            f"Machining\n"
            f"  Material : {self.material}\n"
            f"  RPM      : {self.rpm}\n"
            f"  Depth    : {self.depth} mm\n"
            f"  Tool     : {self.tool}"
        )