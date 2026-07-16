from units import normalize_angle


def handle(command, robot_state):
    position = command.args.get("position")

    if position is None:
        return "Target position is missing"

    for key in ("x", "y", "z"):
        if key in position and position[key] is not None:
            robot_state.target_position[key] = position[key]

    return f"Target position updated: {robot_state.target_position}"