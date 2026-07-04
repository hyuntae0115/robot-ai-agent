from datetime import datetime


def log_command(user_input: str, result: str) -> None:
    with open("robot_log.txt", "a", encoding="utf-8") as file:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{now}] input={user_input} | result={result}\n")