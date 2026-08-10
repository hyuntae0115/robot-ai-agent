def handle(command, robot_state):
    position = command.args.get("position")

    if position is None:
        return "Target position is missing"

    for key in ("x", "y", "z"):
        value = position.get(key)

        if value is not None:
            robot_state.target_position[key] = value

    return (
        "Target position updated: "
        f"{robot_state.target_position}"
    )