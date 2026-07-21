import re


# 한 자리 한글 숫자
KOREAN_DIGITS = {
    "영": 0,
    "공": 0,
    "일": 1,
    "이": 2,
    "삼": 3,
    "사": 4,
    "오": 5,
    "육": 6,
    "륙": 6,
    "칠": 7,
    "팔": 8,
    "구": 9,
}


# 하나, 둘과 같은 고유어 숫자
NATIVE_KOREAN_NUMBERS = {
    "하나": 1,
    "한": 1,
    "둘": 2,
    "두": 2,
    "셋": 3,
    "세": 3,
    "넷": 4,
    "네": 4,
}


# 십진 단위
SMALL_UNITS = {
    "십": 10,
    "백": 100,
    "천": 1000,
}


# Whisper가 인식할 수 있는 좌표축 표현
AXIS_ALIASES : dict[str, str] = {
    "엑스": "x",
    "액스": "x",
    "x": "x",

    "와이": "y",
    "y": "y",

    "지": "z",
    "제트": "z",
    "젯": "z",
    "z": "z",
}


# 좌표축 표현을 x, y, z로 통일한다.
AXIS_PATTERN = re.compile(
    r"(?<![가-힣a-zA-Z0-9])"
    r"(엑스|액스|와이|제트|젯|지|[xyzXYZ])"
    r"\s*(?:축|좌표)?",
    re.IGNORECASE,
)


# 좌표값 패턴
#
# 인식 가능한 예:
# x는 300
# x 좌표는 삼백
# 와이 축 값은 백오십 밀리미터
# 제트 좌표 오십 mm
COORDINATE_PATTERN = re.compile(
    r"(?P<axis>[xyzXYZ])"
    r"\s*(?:축|좌표)?"
    r"\s*(?:값)?"
    r"\s*(?:은|는|이|가)?"
    r"\s*(?P<sign>마이너스|음수|-)?"
    r"\s*(?P<number>"
    r"\d+(?:\.\d+)?"
    r"|"
    r"(?:영|공|일|이|삼|사|오|육|륙|칠|팔|구|십|백|천|만|"
    r"하나|한|둘|두|셋|세|넷|네|[0-9]|\s)+"
    r")"
    r"\s*(?P<unit>"
    r"밀리미터|미리미터|미리|mm|"
    r"센티미터|cm|"
    r"미터|m"
    r")?",
    re.IGNORECASE,
)


def normalize_axis_words(text: str) -> str:
    """
    음성 인식 결과에 포함된 좌표축 표현을
    x, y, z로 통일한다.

    예:
        엑스 좌표 -> x
        와이 축   -> y
        제트 좌표 -> z
    """

    def replace_axis(match: re.Match[str]) -> str:
        axis_word = match.group(1).lower()
        return AXIS_ALIASES.get(axis_word, axis_word)

    return AXIS_PATTERN.sub(replace_axis, text)


def korean_number_to_int(number_text: str) -> int | float | None:
    """
    한글 숫자 표현을 정수 또는 실수로 변환한다.

    예:
        삼백     -> 300
        백오십   -> 150
        오십     -> 50
        3백      -> 300
        하나     -> 1
        150      -> 150
        12.5     -> 12.5
    """

    number_text = number_text.replace(" ", "").strip()

    if not number_text:
        return None

    # 이미 아라비아 숫자인 경우
    if re.fullmatch(r"\d+", number_text):
        return int(number_text)

    if re.fullmatch(r"\d+\.\d+", number_text):
        return float(number_text)

    # 하나, 둘, 셋 등의 고유어 숫자
    if number_text in NATIVE_KOREAN_NUMBERS:
        return NATIVE_KOREAN_NUMBERS[number_text]

    tokens = re.findall(
        r"\d+|[영공일이삼사오육륙칠팔구]|[십백천만]",
        number_text,
    )

    if not tokens:
        return None

    total = 0
    section_total = 0
    current_number = 0

    for token in tokens:
        # 3백처럼 아라비아 숫자가 포함된 경우
        if token.isdigit():
            current_number = int(token)
            continue

        # 영, 일, 이, 삼 등의 숫자
        if token in KOREAN_DIGITS:
            current_number = KOREAN_DIGITS[token]
            continue

        # 십, 백, 천
        if token in SMALL_UNITS:
            unit_value = SMALL_UNITS[token]

            # 백, 십처럼 앞 숫자가 생략되면 1로 처리
            if current_number == 0:
                current_number = 1

            section_total += current_number * unit_value
            current_number = 0
            continue

        # 만 단위
        if token == "만":
            section_value = section_total + current_number

            if section_value == 0:
                section_value = 1

            total += section_value * 10000
            section_total = 0
            current_number = 0

    return total + section_total + current_number


def normalize_unit(unit: str | None) -> str:
    """
    음성 인식 결과에 포함된 단위 표현을 통일한다.
    """

    if not unit:
        return ""

    unit = unit.lower()

    unit_aliases = {
        "밀리미터": "mm",
        "미리미터": "mm",
        "미리": "mm",
        "mm": "mm",

        "센티미터": "cm",
        "cm": "cm",

        "미터": "m",
        "m": "m",
    }

    return unit_aliases.get(unit, unit)


def normalize_voice_command(text: str) -> str:
    """
    Whisper 음성 인식 결과에 포함된 좌표축과 숫자를 정규화한다.

    예:
        엑스 좌표는 삼백 밀리미터,
        와이 좌표는 백오십 밀리미터,
        제트 좌표는 오십 밀리미터로 이동해

    결과:
        x는 300 mm, y는 150 mm, z는 50 mm로 이동해
    """

    # 1. 좌표축 표현 통일
    normalized_text = normalize_axis_words(text)

    # 2. 좌표값과 숫자 표현 통일
    def replace_coordinate(match: re.Match) -> str:
        axis = match.group("axis").lower()
        sign = match.group("sign")
        number_text = match.group("number")
        unit_text = match.group("unit")

        number = korean_number_to_int(number_text)

        # 숫자 변환에 실패하면 원문을 유지한다.
        if number is None:
            return match.group(0)

        if sign in {"마이너스", "음수", "-"}:
            number = -number

        unit = normalize_unit(unit_text)

        if unit:
            return f"{axis}는 {number} {unit}"

        return f"{axis}는 {number}"

    normalized_text = COORDINATE_PATTERN.sub(
        replace_coordinate,
        normalized_text,
    )

    # 3. 불필요한 공백 정리
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()

    return normalized_text


if __name__ == "__main__":
    test_commands = [
        (
            "엑스 좌표는 삼백 밀리미터, "
            "와이 좌표는 백오십 밀리미터, "
            "제트 좌표는 오십 밀리미터로 이동한 뒤 "
            "알루미늄에 직경 육 밀리미터로 구멍을 뚫어줘."
        ),
        "액스 3백, 와이 150, 지 50으로 이동해.",
        "x 좌표는 마이너스 백, y 좌표는 이백, z 좌표는 삼십 mm로 이동해.",
    ]

    for command in test_commands:
        print("변환 전:", command)
        print("변환 후:", normalize_voice_command(command))
        print()