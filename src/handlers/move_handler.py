def handle(command, robot_state):
    direction = command.args[0]
    distance = command.args[1]

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

    robot_state.is_moving = True

    return f"Moved {direction} by {distance} mm"