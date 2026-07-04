class RobotState:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.is_moving = False

    def get_status(self) -> str:
        return f"Position: x={self.x}, y={self.y}, z={self.z}, moving={self.is_moving}"