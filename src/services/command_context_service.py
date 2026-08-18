from command import Command


# 이 값이 변경되면 기존 RPM과 Feed 추천을
# 다시 사용하면 안 된다.
RECOMMENDATION_INPUT_FIELDS = {
    "material",
    "depth",
    "diameter",
}


def merge_command(
    command,
    command_context,
):
    if command.name == "target":
        _merge_target_command(
            command,
            command_context,
        )

    elif command.name == "machine":
        _merge_machine_command(
            command,
            command_context,
        )


def _merge_target_command(
    command,
    command_context,
):
    position = (
        command.args.get("position")
        or {}
    )

    target_changed = False

    for key, value in position.items():
        if key not in (
            command_context.pending_target
        ):
            continue

        if value is None:
            continue

        previous_value = (
            command_context
            .pending_target[key]
        )

        if previous_value == value:
            continue

        command_context.pending_target[key] = (
            value
        )

        target_changed = True

    # X, Y, Z는 RPM·Feed 추천 입력이 아니므로
    # 추천 결과는 유지한다.
    #
    # 다만 로봇 자세와 관절각이 달라지므로
    # Isaac Sim 결과만 초기화한다.
    if target_changed:
        command_context.invalidate_simulation()


def _merge_machine_command(
    command,
    command_context,
):
    # 현재 명령에서 실제 값이 들어온 필드만 추출한다.
    updates = {
        key: value
        for key, value in (
            command.args.items()
        )
        if (
            key
            in command_context.pending_machine
            and value is not None
        )
    }

    if not updates:
        return

    changed_fields = {
        key
        for key, value in updates.items()
        if (
            command_context
            .pending_machine.get(key)
            != value
        )
    }

    if not changed_fields:
        return

    recommendation_input_changed = bool(
        changed_fields
        & RECOMMENDATION_INPUT_FIELDS
    )

    if recommendation_input_changed:
        # 소재·깊이·직경 중 하나라도 변경되면
        # 기존 RPM·Feed·공구 추천을 삭제한다.
        command_context.invalidate_recommendation()

    else:
        # 그 외 가공조건이 변경돼도
        # 기존 Isaac Sim 결과는 무효다.
        command_context.invalidate_simulation()

    # 초기화 이후 현재 명령에 명시된 값을 적용한다.
    #
    # 예:
    # "깊이는 7mm, 공구는 드릴로 바꿔줘"
    #
    # 먼저 기존 추천 RPM·Feed·공구를 초기화한 다음
    # depth=7과 tool=drill을 다시 적용한다.
    for key, value in updates.items():
        command_context.pending_machine[key] = (
            value
        )


def build_commands(
    command_context,
):
    target_command = Command(
        "target",
        position=(
            command_context
            .pending_target.copy()
        ),
    )

    machine_command = Command(
        "machine",
        **(
            command_context
            .pending_machine.copy()
        ),
    )

    return [
        target_command,
        machine_command,
    ]