from controller import handle_user_input


def run_console(robot_state):
    print("Robot AI Agent started.")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            print("명령을 입력하세요.")
            continue

        results, _ = handle_user_input(
            user_input,
            robot_state
        )

        for result in results:
            print(result)