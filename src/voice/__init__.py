from voice.normalizer import normalize_voice_command
from voice.recognizer import transcribe_audio
from voice.recorder import record_until_silence


def listen_voice() -> str:
    audio = record_until_silence()

    if audio is None:
        return ""

    raw_text = transcribe_audio(audio)
    normalized_text = normalize_voice_command(raw_text)

    print(f"Whisper result: {raw_text}")
    print(f"Normalized result: {normalized_text}")

    return normalized_text