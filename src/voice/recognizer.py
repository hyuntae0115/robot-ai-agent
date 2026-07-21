import os
import tempfile

import numpy as np
import scipy.io.wavfile as wav
import whisper

from voice.recorder import SAMPLE_RATE


model = whisper.load_model("base")


def transcribe_audio(audio: np.ndarray) -> str:
    audio_path = None

    try:
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

        print("음성을 인식하는 중입니다.")

        result = model.transcribe(
            audio_path,
            language="ko",
            fp16=False,
            initial_prompt=(
                "로봇 가공 명령입니다. "
                "x, y, z 좌표와 RPM, 재료, 깊이, 공구를 말합니다. "
                "예시: x는 1, y는 2, z는 3에서 "
                "3000 RPM으로 알루미늄을 가공해줘."
            )
        )

        text = result["text"].strip()  # type: ignore

        return text

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)