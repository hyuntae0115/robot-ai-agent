def handle(command, robot_state):

    axis = command.args[0]
    angle = command.args[1]

    if axis == "x":
        robot_state.roll = robot_state.normalize_angle(
            robot_state.roll + angle
        )

    elif axis == "y":
        robot_state.pitch = robot_state.normalize_angle(
            robot_state.pitch + angle
        )

    elif axis == "z":
        robot_state.yaw = robot_state.normalize_angle(
            robot_state.yaw + angle
        )

    return f"Rotated {axis} axis by {angle}°"