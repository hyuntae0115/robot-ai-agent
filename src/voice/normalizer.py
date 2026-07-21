import re


KOREAN_NUMBERS = {
    "영": "0",
    "공": "0",
    "일": "1",
    "하나": "1",
    "한": "1",
    "이": "2",
    "둘": "2",
    "두": "2",
    "삼": "3",
    "셋": "3",
    "세": "3",
    "사": "4",
    "넷": "4",
    "네": "4",
    "오": "5",
    "육": "6",
    "륙": "6",
    "칠": "7",
    "팔": "8",
    "구": "9",
}


COORDINATE_PATTERN = re.compile(
    r"\b([xyzXYZ])\s*"
    r"(?:는|은|가|값은|값이)?\s*"
    r"(영|공|일|하나|한|이|둘|두|삼|셋|세|사|넷|네|오|육|륙|칠|팔|구)\b"
)


def normalize_voice_command(text: str) -> str:
    def replace_coordinate(match: re.Match) -> str:
        axis = match.group(1).lower()
        number_word = match.group(2)
        number = KOREAN_NUMBERS[number_word]

        return f"{axis}는 {number}"

    normalized_text = COORDINATE_PATTERN.sub(
        replace_coordinate,
        text
    )

    return normalized_text