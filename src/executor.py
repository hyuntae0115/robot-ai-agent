def execute(parsed_command: dict, robot_state) -> str:
    if not parsed_command["valid"]:
        return parsed_command["error"]

    command = parsed_command["command"]

    name = command.name
    args = command.args

    if name == "move":
        direction = args[0]
        distance = args[1]

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
        return f"Moved {direction} by {distance} cm"

    if name == "stop":
        robot_state.is_moving = False
        return "Robot stopped"

    if name == "status":
        return robot_state.get_status()

    return "Execution failed"