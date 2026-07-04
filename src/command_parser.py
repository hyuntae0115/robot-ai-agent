from command import Command

VALID_DIRECTIONS = ["forward", "backward", "left", "right", "up", "down"]


def parse_command(user_input: str) -> dict:
    parts = user_input.strip().split()

    if not parts:
        return {"valid": False, "error": "Empty command"}

    command = parts[0]
    args = parts[1:]

    if command == "status":
        if len(args) != 0:
            return {"valid": False, "error": "status requires 0 arguments"}

        return {
            "valid": True,
            "command": Command("status", [])
        }

    if command == "stop":
        if len(args) != 0:
            return {"valid": False, "error": "stop requires 0 arguments"}

        return {
            "valid": True,
            "command": Command("stop", [])
        }

    if command == "move":
        if len(args) != 2:
            return {"valid": False, "error": "move requires 2 arguments"}

        direction = args[0]
        distance = args[1]

        if direction not in VALID_DIRECTIONS:
            return {
                "valid": False,
                "error": f"Invalid direction: {direction}"
            }

        if not distance.isdigit():
            return {
                "valid": False,
                "error": f"Distance must be a number: {distance}"
            }

        return {
            "valid": True,
            "command": Command(
                "move",
                [direction, int(distance)]
            )
        }

    return {
        "valid": False,
        "error": f"Unknown command: {command}"
    }