import os
import tempfile
from collections.abc import Callable
from typing import Any

import numpy as np
import scipy.io.wavfile as wav
import whisper

from voice.recorder import SAMPLE_RATE


StatusCallback = Callable[[str], None]


def send_status(
    status_callback: StatusCallback | None,
    message: str
) -> None:
    """
    상태 콜백이 있으면 GUI에 현재 처리 상태를 전달한다.
    """
    if status_callback is not None:
        status_callback(message)


# Whisper 모델은 음성 인식마다 다시 생성하지 않고
# recognizer.py가 처음 불러와질 때 한 번만 생성한다.
print("Whisper 모델을 불러오는 중입니다.")
model = whisper.load_model("base")
print("Whisper 모델 로딩이 완료되었습니다.")


def transcribe_audio(
    audio: np.ndarray,
    status_callback: StatusCallback | None = None
) -> str:
    """
    녹음된 NumPy 오디오 데이터를 임시 WAV 파일로 저장하고,
    Whisper를 이용해 한국어 문장으로 변환한다.

    Args:
        audio:
            recorder.py에서 녹음한 오디오 배열

        status_callback:
            GUI에 현재 처리 상태를 전달하는 함수

    Returns:
        Whisper가 인식한 원본 문자열.
        인식에 실패하면 빈 문자열을 반환한다.
    """
    audio_path: str | None = None

    try:
        if audio.size == 0:
            print("인식할 오디오 데이터가 없습니다.")

            send_status(
                status_callback,
                "인식할 음성 데이터가 없습니다."
            )

            return ""

        send_status(
            status_callback,
            "음성을 문자로 변환하고 있습니다.\n"
            "잠시 기다려주세요."
        )

        print("음성을 문자로 변환하는 중입니다.")

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:
            audio_path = temp_file.name

        wav.write(
            audio_path,
            SAMPLE_RATE,
            audio
        )

        result: dict[str, Any] = model.transcribe(
            audio_path,
            language="ko",
            fp16=False,
            initial_prompt=(
                "CNC 로봇 가공 명령입니다. "
                "사용자는 x, y, z 좌표와 재료, RPM, "
                "가공 깊이, 공구 종류를 말합니다. "
                "공구 종류는 엔드밀, 드릴, 볼밀, 탭입니다. "
                "엔드밀이라는 전문용어를 정확하게 인식하세요. "
                "예시 문장은 다음과 같습니다. "
                "x는 1, y는 2, z는 3에서 "
                "3000 RPM으로 엔드밀을 사용해 "
                "알루미늄을 가공해줘."
            )
        )

        text = str(result.get("text", "")).strip()

        if not text:
            print("Whisper가 음성을 인식하지 못했습니다.")

            send_status(
                status_callback,
                "음성을 문자로 변환하지 못했습니다.\n"
                "다시 시도해주세요."
            )

            return ""

        print(f"Whisper result: {text}")

        send_status(
            status_callback,
            "음성 인식이 완료되었습니다."
        )

        return text

    except Exception as error:
        print(f"음성 인식 오류: {error}")

        send_status(
            status_callback,
            "음성 인식 중 오류가 발생했습니다.\n"
            f"{error}"
        )

        return ""

    finally:
        if (
            audio_path is not None
            and os.path.exists(audio_path)
        ):
            try:
                os.remove(audio_path)

            except OSError as error:
                print(
                    "임시 음성 파일을 삭제하지 못했습니다: "
                    f"{error}"
                )