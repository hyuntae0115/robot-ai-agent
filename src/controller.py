from agent import process
from executor import execute
from logger import log_command

from services.command_context_service import build_commands, merge_command
from services.command_validation_service import (
    find_first_missing_field,
    make_clarification_question,
)
from services.machining_recommendation_service import (
    recommend_missing_conditions,
)


def handle_user_input(user_input, robot_state, command_context):
    expected_field = find_first_missing_field(command_context)
    parsed_commands, raw_output = process(
        user_input,
        expected_field=expected_field,
    )

    results = []
    task_command_received = False

    for parsed in parsed_commands:
        if not parsed["valid"]:
            results.append(parsed["error"])
            continue

        command = parsed["command"]

        if command.name in ("target", "machine"):
            merge_command(command, command_context)
            task_command_received = True
            continue

        if command.name in ("status", "stop"):
            result = execute(command, robot_state)
            log_command(user_input, result)
            results.append(result)

    if not task_command_received:
        return results, raw_output

    missing_field = find_first_missing_field(command_context)
    if missing_field is not None:
        results.append(make_clarification_question(missing_field))
        return results, raw_output

    recommendation = recommend_missing_conditions(
        command_context.pending_machine
    )
    if recommendation is not None and recommendation.changed:
        results.append(recommendation.to_message())

    results.append(
        "필수 작업정보가 모두 입력되었습니다.\n"
        "내용을 확인한 뒤 작업 실행 버튼을 눌러주세요."
    )
    return results, raw_output


def execute_pending_command(robot_state, command_context):
    missing_field = find_first_missing_field(command_context)
    if missing_field is not None:
        return [make_clarification_question(missing_field)]

    # 분석 직후가 아닌 다른 경로로 실행해도 추천값이 빠지지 않게 보장한다.
    recommend_missing_conditions(command_context.pending_machine)
    commands = build_commands(command_context)
    results = []

    try:
        for command in commands:
            result = execute(command, robot_state)
            log_command("GUI 작업 실행", result)
            results.append(result)
    except Exception:
        raise

    command_context.apply_pending()
    command_context.clear_pending()
    return results
