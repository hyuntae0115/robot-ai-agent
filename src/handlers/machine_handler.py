from services.machine_setting_service import update_machine_settings


def handle(command, robot_state):
    update_machine_settings(command, robot_state)

    return (
        f"Machine setting updated\n"
        f"Position: {robot_state.target_position}\n"
        f"Material: {robot_state.material}\n"
        f"Process: {robot_state.process}\n"
         f"Tool: {robot_state.tool}\n"
        f"Diameter: {robot_state.diameter} mm\n"
        f"Depth: {robot_state.depth} mm\n"
        f"RPM: {robot_state.rpm} RPM"
    )