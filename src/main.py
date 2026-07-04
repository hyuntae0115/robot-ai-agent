from command_parser import parse_command
from executor import execute
from robot_state import RobotState
from logger import log_command


def main():
    robot_state = RobotState()

    print("Robot AI Agent started.")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("> ")

        if user_input == "exit":
            print("Program ended.")
            break

        parsed = parse_command(user_input)
        result = execute(parsed, robot_state)

        log_command(user_input, result)

        print(result)


if __name__ == "__main__":
    main()