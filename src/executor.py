from handlers.move_handler import handle as move_handle
from handlers.status_handler import handle as status_handle
from handlers.stop_handler import handle as stop_handle
from handlers.rotate_handler import handle as rotate_handle


HANDLERS = {
    "move": move_handle,
    "status": status_handle,
    "stop": stop_handle,
    "rotate": rotate_handle
}   


def execute(parsed_command: dict, robot_state) -> str:
    if not parsed_command["valid"]:
        return parsed_command["error"]

    command = parsed_command["command"]

    handler = HANDLERS.get(command.name)

    if handler is None:
        return f"No handler found for command: {command.name}"

    return handler(command, robot_state)