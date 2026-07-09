class RobotState:
    def __init__(self):
        # 현재 TCP pose
        self.x = 0
        self.y = 0
        self.z = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        # 가공 목표 pose
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

        self.is_moving = False

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle

    def get_status(self):
        pose = self.target_pose

        return (
            f"Current Pose: "
            f"x={self.x} mm, "
            f"y={self.y} mm, "
            f"z={self.z} mm, "
            f"roll={self.roll}°, "
            f"pitch={self.pitch}°, "
            f"yaw={self.yaw}°\n"
            f"Target Pose: "
            f"x={pose['x']} mm, "
            f"y={pose['y']} mm, "
            f"z={pose['z']} mm, "
            f"roll={pose['roll']}°, "
            f"pitch={pose['pitch']}°, "
            f"yaw={pose['yaw']}°\n"
            f"Material: {self.material}\n"
            f"RPM: {self.rpm}\n"
            f"Depth: {self.depth} mm\n"
            f"Tool: {self.tool}\n"
            f"Moving: {self.is_moving}"
        )