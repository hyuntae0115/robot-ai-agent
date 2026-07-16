def handle(command, robot_state):
    position = command.args.get("position")
    material = command.args.get("material")
    rpm = command.args.get("rpm")
    depth = command.args.get("depth")
    tool = command.args.get("tool")
    diameter = command.args.get("diameter")

    if position is not None:
        robot_state.target_position = position

    if material is not None:
        robot_state.material = material

    if rpm is not None:
        robot_state.rpm = rpm

    if depth is not None:
        robot_state.depth = depth

    if tool is not None:
        robot_state.tool = tool

    if diameter is not None:
        robot_state.diameter= diameter

    return (
        f"Machine setting updated\n"
        f"position: {robot_state.target_position}\n"
        f"Material: {robot_state.material}\n"
        f"RPM: {robot_state.rpm}\n"
        f"Depth: {robot_state.depth} mm\n"
        f"Tool: {robot_state.tool}\n"
        f"diameter: {robot_state.diameter} mm"
    )