from handlers.target_handler import handle as target_handle
from handlers.status_handler import handle as status_handle
from handlers.stop_handler import handle as stop_handle
from handlers.machine_handler import handle as machine_handle


HANDLERS = {
    "target": target_handle,
    "status": status_handle,
    "stop": stop_handle,
    "machine": machine_handle
}


def execute(command, robot_state) -> str:
    handler = HANDLERS.get(command.name)

    if handler is None:
        return f"No handler found for command: {command.name}"

    return handler(command, robot_state)