from command import Command

def merge_command(command, command_context):
    if command.name == "target":
        position = command.args.get("position") or {}

        for key, value in position.items():
            if (
                key in command_context.pending_target
                and value is not None
            ):
                command_context.pending_target[key] = value

    elif command.name == "machine":
        for key, value in command.args.items():
            if (
                key in command_context.pending_machine
                and value is not None
            ):
                command_context.pending_machine[key] = value


def build_commands(command_context):
    target_command = Command(
        name="target",
        args={
            "position": command_context.pending_target.copy()
        }
    )

    machine_command = Command(
        name="machine",
        args=command_context.pending_machine.copy()
    )

    return [
        target_command,
        machine_command
    ]