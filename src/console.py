from robot_state import RobotState
from controller import handle_user_input


def main():
    robot_state = RobotState()

    print("Robot AI Agent started.")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("> ")

        if user_input == "exit":
            break

        results = handle_user_input(user_input, robot_state)

        for result in results:
            print(result)


if __name__ == "__main__":
    main()