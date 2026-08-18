TARGET_REQUIRED_FIELDS = (
    "x",
    "y",
    "z",
)

SUPPORTED_MATERIALS = {
    "aluminum",
    "stainless_steel",
    "titanium",
    "iron",
    "UD_CFRP",
}

FIELD_QUESTIONS = {
    ("target", "x"): "X 좌표를 입력해주세요.",
    ("target", "y"): "Y 좌표를 입력해주세요.",
    ("target", "z"): "Z 좌표를 입력해주세요.",
    (
        "machine",
        "material",
    ): (
        "소재가 입력되지 않았거나 지원하지 않는 소재입니다.\n"
        "지원 소재: aluminum, stainless_steel, titanium, iron, UD_CFRP"
    ),
    ("machine", "depth"): "가공 깊이를 입력해주세요.",
}


def find_first_missing_field(command_context):
    # 위치 필수값 검사
    for field in TARGET_REQUIRED_FIELDS:
        if command_context.pending_target.get(field) is None:
            return "target", field

    # 소재 입력 및 지원 여부 검사
    material = command_context.pending_machine.get("material")

    if material not in SUPPORTED_MATERIALS:
        return "machine", "material"

    # 가공 깊이 검사
    if command_context.pending_machine.get("depth") is None:
        return "machine", "depth"

    return None


def make_clarification_question(missing_field):
    return FIELD_QUESTIONS[missing_field]