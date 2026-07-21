from collections.abc import Callable

from voice.normalizer import normalize_voice_command
from voice.recognizer import transcribe_audio
from voice.recorder import record_until_silence


StatusCallback = Callable[[str], None]


def listen_voice(
    status_callback: StatusCallback | None = None
) -> tuple[str, str]:
    audio = record_until_silence(
        status_callback=status_callback
    )

    if audio is None:
        return "", ""

    raw_text = transcribe_audio(
        audio,
        status_callback=status_callback
    )

    if not raw_text:
        return "", ""

    normalized_text = normalize_voice_command(raw_text)

    if status_callback is not None:
        status_callback(
            "음성 인식이 완료되었습니다.\n"
            f"인식 결과: {raw_text}"
        )

    print(f"Whisper result: {raw_text}")
    print(f"Normalized result: {normalized_text}")

    return raw_text, normalized_text