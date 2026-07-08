from executor import execute
from logger import log_command
from agent import process


def handle_user_input(user_input, robot_state):
    parsed_commands, raw_output = process(user_input)

    results = []

    for parsed in parsed_commands:
        if not parsed["valid"]:
            results.append(parsed["error"])
            continue

        command = parsed["command"]

        result = execute(command, robot_state)
        log_command(user_input, result)
        results.append(result)

    return results, raw_output