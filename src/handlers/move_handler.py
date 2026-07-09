def handle(command, robot_state):
    direction = command.args["direction"]
    distance = command.args["distance"]

    if direction == "forward":
        robot_state.y += distance

    elif direction == "backward":
        robot_state.y -= distance

    elif direction == "right":
        robot_state.x += distance

    elif direction == "left":
        robot_state.x -= distance

    elif direction == "up":
        robot_state.z += distance

    elif direction == "down":
        robot_state.z -= distance

    else:
        return f"Unknown move direction: {direction}"

    robot_state.is_moving = True

    return f"Moved {direction} by {distance} mm"