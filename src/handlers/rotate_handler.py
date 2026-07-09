def handle(command, robot_state):
    axis = command.args["axis"]
    angle = command.args["angle"]

    if axis == "x":
        robot_state.roll = robot_state.normalize_angle(robot_state.roll + angle)

    elif axis == "y":
        robot_state.pitch = robot_state.normalize_angle(robot_state.pitch + angle)

    elif axis == "z":
        robot_state.yaw = robot_state.normalize_angle(robot_state.yaw + angle)

    else:
        return f"Unknown rotation axis: {axis}"

    return f"Rotated {axis} axis by {angle}°"