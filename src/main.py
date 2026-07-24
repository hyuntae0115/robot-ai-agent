from machining_settings import MachiningSettings
from interfaces.console import run_console
from interfaces.test_gui import run_gui
from command_context import CommandContext
    
def main():
    machining_settings = MachiningSettings()
    command_context = CommandContext()

    mode = input(
        "실행 모드 선택 [console/gui]: "
    ).strip().lower()

    if mode == "console":
        run_console(machining_settings, command_context)

    elif mode == "gui":
        run_gui(machining_settings, command_context)

    else:
        print("지원하지 않는 실행 모드입니다.")


if __name__ == "__main__":
    main()