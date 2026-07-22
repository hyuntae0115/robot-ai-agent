import re


# ============================================================
# 숫자 관련 설정
# ============================================================

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


# ============================================================
# Whisper 전문용어 오인식 보정
# ============================================================

# 실제 Whisper 원본에서 반복적으로 발생한 오인식만
# 여기에 추가하는 방식으로 관리한다.
VOICE_TERM_ALIASES: dict[str, str] = {
    # ---------------- 공구 ---------------- #

    # 엔드밀
    "핸드 미리": "엔드밀",
    "핸드미리": "엔드밀",
    "핸드 밀": "엔드밀",
    "핸드밀": "엔드밀",
    "앤드 미리": "엔드밀",
    "앤드미리": "엔드밀",
    "앤드 밀": "엔드밀",
    "앤드밀": "엔드밀",
    "엔드 미리": "엔드밀",
    "엔드미리": "엔드밀",
    "엔드 밀": "엔드밀",
    "end mill": "엔드밀",
    "endmill": "엔드밀",

    # 볼엔드밀
    "볼 핸드 밀": "볼엔드밀",
    "볼 핸드밀": "볼엔드밀",
    "볼 앤드 밀": "볼엔드밀",
    "볼 앤드밀": "볼엔드밀",
    "볼 엔드 밀": "볼엔드밀",
    "볼 엔드밀": "볼엔드밀",
    "볼엔드 밀": "볼엔드밀",
    "볼 밀": "볼엔드밀",
    "볼밀": "볼엔드밀",
    "ball end mill": "볼엔드밀",
    "ball mill": "볼엔드밀",
    "ballmill": "볼엔드밀",

    # 드릴
    "드릴링 비트": "드릴",
    "드릴 비트": "드릴",
    "드릴비트": "드릴",
    "드릴 빗": "드릴",
    "드릴빗": "드릴",
    "drill bit": "드릴",
    "drill": "드릴",

    # 탭
    "태핑 공구": "탭",
    "테핑 공구": "탭",
    "탭 공구": "탭",

    # ---------------- 재료 ---------------- #

    # 알루미늄
    "루이미늄의": "알루미늄에",
    "루미늄의": "알루미늄에",
    "알미늄의": "알루미늄에",
    "아루미늄의": "알루미늄에",
    "알류미늄의": "알루미늄에",
    "알루미늄의": "알루미늄에",

    "루이미늄": "알루미늄",
    "루미늄": "알루미늄",
    "알미늄": "알루미늄",
    "아루미늄": "알루미늄",
    "알류미늄": "알루미늄",

    # 티타늄
    "히타늄": "티타늄",
    "타이타늄": "티타늄",
    "티타니움": "티타늄",
    "타이타니엄": "티타늄",

    # 스테인리스
    "스테인레스 스틸": "스테인리스강",
    "스테인리스 스틸": "스테인리스강",
    "스테인레스강": "스테인리스강",
    "스텐레스강": "스테인리스강",
    "스텐리스강": "스테인리스강",
    "스테인레스": "스테인리스",
    "스텐레스": "스테인리스",
    "스텐리스": "스테인리스",

    # 탄소강
    "탄소 강": "탄소강",

    # ---------------- 가공 표현 ---------------- #

    "공항을 뚫어 줘": "구멍을 뚫어줘",
    "공항을 뚫어줘": "구멍을 뚫어줘",
    "공항 뚫어 줘": "구멍 뚫어줘",
    "공항 뚫어줘": "구멍 뚫어줘",

    "구멍을 뚜러 줘": "구멍을 뚫어줘",
    "구멍을 뚜러줘": "구멍을 뚫어줘",
    "구멍을 뚤어 줘": "구멍을 뚫어줘",
    "구멍을 뚤어줘": "구멍을 뚫어줘",

    "이동한지": "이동한 뒤",
    "이동 한지": "이동한 뒤",
    "이동한 후에": "이동한 뒤",

    "드릴링 해 줘": "드릴링해줘",
    "드릴링 해줘": "드릴링해줘",
    "밀링 해 줘": "밀링해줘",
    "밀링 해줘": "밀링해줘",
    "태핑 해 줘": "태핑해줘",
    "태핑 해줘": "태핑해줘",
    "테핑해줘": "태핑해줘",

    # ---------------- 치수 용어 ---------------- #

    "식 경": "직경",
    "식경": "직경",
    "지 경": "직경",
    "지경": "직경",
    "직 경": "직경",

    "깁이": "깊이",
    "기피": "깊이",

    # ---------------- 단위 표현 ---------------- #

    "미리 미터": "밀리미터",
    "미리미터": "밀리미터",
    "밀리 미터": "밀리미터",

    "센치미터": "센티미터",
    "센치 미터": "센티미터",

    "알 피 엠": "rpm",
    "알피엠": "rpm",
}


def replace_voice_term_aliases(text: str) -> str:
    """
    Whisper가 잘못 인식한 전문용어와 고정 표현을 보정한다.

    긴 표현을 먼저 치환한다.

    예:
        루이미늄의 -> 알루미늄에
        루이미늄   -> 알루미늄

    짧은 표현을 먼저 치환하면 긴 표현을 처리하지 못할 수 있으므로
    문자열 길이를 기준으로 내림차순 정렬한다.
    """

    normalized_text = text

    sorted_aliases = sorted(
        VOICE_TERM_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for wrong_text, correct_text in sorted_aliases:
        normalized_text = normalized_text.replace(
            wrong_text,
            correct_text,
        )

    return normalized_text


# ============================================================
# 좌표축 관련 설정
# ============================================================

# Whisper가 인식할 수 있는 좌표축 표현
AXIS_ALIASES: dict[str, str] = {
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


# 숫자 표현에 사용되는 공통 정규식
KOREAN_NUMBER_PATTERN = (
    r"\d+(?:\.\d+)?"
    r"|"
    r"(?:영|공|일|이|삼|사|오|육|륙|칠|팔|구|"
    r"십|백|천|만|"
    r"하나|한|둘|두|셋|세|넷|네|"
    r"[0-9]|\s)+"
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
    + KOREAN_NUMBER_PATTERN
    + r")"
    r"\s*(?P<unit>"
    r"밀리미터|미리미터|미리|mm|"
    r"센티미터|센치미터|cm|"
    r"미터|m"
    r")?",
    re.IGNORECASE,
)


# 직경 및 깊이 패턴
#
# 인식 가능한 예:
# 직경 육 밀리미터
# 직경 6mm
# 깊이 십오 밀리미터
# 깊이는 15 mm
MEASUREMENT_PATTERN = re.compile(
    r"(?P<label>직경|깊이)"
    r"\s*(?:은|는|이|가)?"
    r"\s*(?P<sign>마이너스|음수|-)?"
    r"\s*(?P<number>"
    + KOREAN_NUMBER_PATTERN
    + r")"
    r"\s*(?P<unit>"
    r"밀리미터|미리미터|미리|mm|"
    r"센티미터|센치미터|cm|"
    r"미터|m"
    r")?",
    re.IGNORECASE,
)


# RPM 패턴
#
# 인식 가능한 예:
# 만이천 rpm
# 만이천 알피엠
# 12000 rpm
# 회전수는 만이천
RPM_PATTERN = re.compile(
    r"(?:(?P<prefix>회전수|rpm)\s*(?:은|는|이|가)?\s*)?"
    r"(?P<number>"
    + KOREAN_NUMBER_PATTERN
    + r")"
    r"\s*(?P<rpm_unit>rpm|알피엠|알 피 엠)",
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


# ============================================================
# 한글 숫자 변환
# ============================================================

def korean_number_to_int(
    number_text: str,
) -> int | float | None:
    """
    한글 숫자 표현을 정수 또는 실수로 변환한다.

    예:
        삼백     -> 300
        백오십   -> 150
        오십     -> 50
        3백      -> 300
        만이천   -> 12000
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


# ============================================================
# 단위 변환
# ============================================================

def normalize_unit(unit: str | None) -> str:
    """
    음성 인식 결과에 포함된 단위 표현을 통일한다.
    """

    if not unit:
        return ""

    unit = unit.lower().replace(" ", "")

    unit_aliases = {
        "밀리미터": "mm",
        "미리미터": "mm",
        "미리": "mm",
        "mm": "mm",

        "센티미터": "cm",
        "센치미터": "cm",
        "cm": "cm",

        "미터": "m",
        "m": "m",
    }

    return unit_aliases.get(unit, unit)


def format_number(number: int | float) -> str:
    """
    6.0처럼 소수 부분이 0인 숫자는 6으로 출력한다.
    """

    if isinstance(number, float) and number.is_integer():
        return str(int(number))

    return str(number)


# ============================================================
# 좌표 정규화
# ============================================================

def normalize_coordinates(text: str) -> str:
    """
    좌표에 포함된 한글 숫자와 단위를 정규화한다.

    예:
        x는 삼백 밀리미터
        -> x는 300 mm
    """

    def replace_coordinate(match: re.Match[str]) -> str:
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

        number_string = format_number(number)
        unit = normalize_unit(unit_text)

        if unit:
            return f"{axis}는 {number_string} {unit}"

        return f"{axis}는 {number_string}"

    return COORDINATE_PATTERN.sub(
        replace_coordinate,
        text,
    )


# ============================================================
# 직경 및 깊이 정규화
# ============================================================

def normalize_measurements(text: str) -> str:
    """
    직경과 깊이에 포함된 한글 숫자 및 단위를 정규화한다.

    예:
        직경 육 밀리미터
        -> 직경 6 mm

        깊이 십오 밀리미터
        -> 깊이 15 mm
    """

    def replace_measurement(match: re.Match[str]) -> str:
        label = match.group("label")
        sign = match.group("sign")
        number_text = match.group("number")
        unit_text = match.group("unit")

        number = korean_number_to_int(number_text)

        if number is None:
            return match.group(0)

        if sign in {"마이너스", "음수", "-"}:
            number = -number

        number_string = format_number(number)
        unit = normalize_unit(unit_text)

        if unit:
            return f"{label} {number_string} {unit}"

        return f"{label} {number_string}"

    return MEASUREMENT_PATTERN.sub(
        replace_measurement,
        text,
    )


# ============================================================
# RPM 정규화
# ============================================================

def normalize_rpm(text: str) -> str:
    """
    RPM에 포함된 한글 숫자를 아라비아 숫자로 변환한다.

    예:
        만이천 알피엠
        -> 12000 rpm

        회전수는 만이천 rpm
        -> 회전수는 12000 rpm
    """

    def replace_rpm(match: re.Match[str]) -> str:
        prefix = match.group("prefix")
        number_text = match.group("number")

        number = korean_number_to_int(number_text)

        if number is None:
            return match.group(0)

        number_string = format_number(number)

        if prefix and prefix.lower() == "회전수":
            return f"회전수는 {number_string} rpm"

        return f"{number_string} rpm"

    return RPM_PATTERN.sub(
        replace_rpm,
        text,
    )


# ============================================================
# 공백 및 문장부호 정리
# ============================================================

def normalize_spacing(text: str) -> str:
    """
    반복 공백과 문장부호 주변의 불필요한 공백을 정리한다.
    """

    normalized_text = re.sub(
        r"\s+",
        " ",
        text,
    )

    normalized_text = re.sub(
        r"\s*,\s*",
        ", ",
        normalized_text,
    )

    normalized_text = re.sub(
        r"\s*\.\s*",
        ". ",
        normalized_text,
    )

    return normalized_text.strip()


# ============================================================
# 최종 정규화 함수
# ============================================================

def normalize_voice_command(text: str) -> str:
    """
    Whisper 음성 인식 결과를 LLM에 전달하기 전에 정규화한다.

    처리 순서:
        1. 전문용어 및 고정 오인식 보정
        2. 좌표축 표현 통일
        3. 좌표 숫자 및 단위 정규화
        4. 직경과 깊이 정규화
        5. RPM 정규화
        6. 불필요한 공백 정리

    중요:
        이 함수는 잘못 인식된 숫자를 추측해서 수정하지 않는다.
        누락된 x, y, z 좌표도 임의로 생성하지 않는다.
    """

    if not text:
        return ""

    normalized_text = text.strip()

    # 1. 전문용어와 고정 오인식 보정
    normalized_text = replace_voice_term_aliases(
        normalized_text,
    )

    # 2. 좌표축 표현 통일
    normalized_text = normalize_axis_words(
        normalized_text,
    )

    # 3. 좌표 숫자 및 단위 정규화
    normalized_text = normalize_coordinates(
        normalized_text,
    )

    # 4. 직경과 깊이 정규화
    normalized_text = normalize_measurements(
        normalized_text,
    )

    # 5. RPM 정규화
    normalized_text = normalize_rpm(
        normalized_text,
    )

    # 6. 공백 정리
    normalized_text = normalize_spacing(
        normalized_text,
    )

    return normalized_text


# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":
    test_commands = [
        (
            "엑스 좌표는 삼백 밀리미터, "
            "와이 좌표는 백오십 밀리미터, "
            "제트 좌표는 오십 밀리미터로 이동한 뒤 "
            "알루미늄에 직경 육 밀리미터로 구멍을 뚫어줘."
        ),

        (
            "액스 3백, 와이 150, 지 50으로 이동해."
        ),

        (
            "x 좌표는 마이너스 백, "
            "y 좌표는 이백, "
            "z 좌표는 삼십 mm로 이동해."
        ),

        (
            "x는 350, z는 50으로 이동한지, "
            "루이미늄의 식경 6mm로 공항을 뚫어줘."
        ),

        (
            "티타늄을 만이천 알피엠으로 "
            "직경 팔 밀리미터 드릴을 사용해서 "
            "깊이 십오 밀리미터로 드릴링해줘."
        ),

        (
            "히타늄을 핸드밀로 밀링 해줘."
        ),

        (
            "알미늄에 볼 앤드 밀을 사용해줘."
        ),
    ]

    for command in test_commands:
        print("=" * 70)
        print("변환 전:", command)
        print("변환 후:", normalize_voice_command(command))
        print()