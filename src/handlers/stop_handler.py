def handle(command, robot_state):
    robot_state.is_moving = False
    return "Robot stopped"