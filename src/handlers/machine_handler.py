def handle(command, robot_state):
    pose = command.args.get("pose")
    material = command.args.get("material")
    rpm = command.args.get("rpm")
    depth = command.args.get("depth")
    tool = command.args.get("tool")

    if pose is not None:
        robot_state.target_pose = pose

    if material is not None:
        robot_state.material = material

    if rpm is not None:
        robot_state.rpm = rpm

    if depth is not None:
        robot_state.depth = depth

    if tool is not None:
        robot_state.tool = tool

    return (
        f"Machine setting updated\n"
        f"Pose: {robot_state.target_pose}\n"
        f"Material: {robot_state.material}\n"
        f"RPM: {robot_state.rpm}\n"
        f"Depth: {robot_state.depth} mm\n"
        f"Tool: {robot_state.tool}"
    )