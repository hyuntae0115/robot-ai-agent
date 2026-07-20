def update_machine_settings(command, robot_state):
    position = command.args.get("position")
    process = command.args.get("process")
    material = command.args.get("material")
    rpm = command.args.get("rpm")
    depth = command.args.get("depth")
    tool = command.args.get("tool")
    diameter = command.args.get("diameter")

    if position is not None:
        robot_state.target_position = position

    if material is not None:
        robot_state.material = material

    process_changed = (
        process is not None
        and robot_state.process is not None
        and process != robot_state.process
    )

    if process_changed:
        robot_state.tool = None
        robot_state.diameter = None
        robot_state.depth = None
        robot_state.rpm = None

    if process is not None:
        robot_state.process = process

    if tool is not None:
        robot_state.tool = tool

    if diameter is not None:
        robot_state.diameter = diameter

    if depth is not None:
        robot_state.depth = depth

    if rpm is not None:
        robot_state.rpm = rpm