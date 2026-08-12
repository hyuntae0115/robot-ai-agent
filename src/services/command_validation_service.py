TARGET_REQUIRED_FIELDS = (
    "x",
    "y",
    "z",
)

MACHINE_REQUIRED_FIELDS = (
    "material",
    "depth",
)

FIELD_QUESTIONS = {
    ("target", "x"): "X 좌표를 입력해주세요.",
    ("target", "y"): "Y 좌표를 입력해주세요.",
    ("target", "z"): "Z 좌표를 입력해주세요.",
    ("machine", "material"): "가공할 재료를 입력해주세요.",
    ("machine", "depth"): "가공 깊이를 입력해주세요.",
}


def find_first_missing_field(command_context):
    for field in TARGET_REQUIRED_FIELDS:
        if command_context.pending_target.get(field) is None:
            return "target", field

    for field in MACHINE_REQUIRED_FIELDS:
        if command_context.pending_machine.get(field) is None:
            return "machine", field

    return None


def make_clarification_question(missing_field):
    return FIELD_QUESTIONS[missing_field]