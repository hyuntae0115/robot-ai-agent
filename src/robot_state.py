class RobotState:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.is_moving = False

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle

    def get_status(self):
        return (
            f"Position: "
            f"x={self.x}, "
            f"y={self.y}, "
            f"z={self.z}, "
            f"roll={self.roll}, "
            f"pitch={self.pitch}, "
            f"yaw={self.yaw}, "
            f"moving={self.is_moving}"
        )