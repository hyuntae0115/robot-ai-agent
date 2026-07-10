from robot_state import RobotState
from interfaces.console import run_console
from interfaces.test_gui import run_gui


def main():
    robot_state = RobotState()

    mode = input(
        "실행 모드 선택 [console/gui]: "
    ).strip().lower()

    if mode == "console":
        run_console(robot_state)

    elif mode == "gui":
        run_gui(robot_state)

    else:
        print("지원하지 않는 실행 모드입니다.")


if __name__ == "__main__":
    main()