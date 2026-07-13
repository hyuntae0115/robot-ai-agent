from units import normalize_angle


def handle(command, robot_state):
    pose = command.args.get("pose")

    if pose is None:
        return "Target pose is missing"

    for key in ("x", "y", "z"):
        if key in pose and pose[key] is not None:
            robot_state.target_pose[key] = pose[key]

    for key in ("roll", "pitch", "yaw"):
        if key in pose and pose[key] is not None:
            robot_state.target_pose[key] = normalize_angle(pose[key])

    return f"Target pose updated: {robot_state.target_pose}"