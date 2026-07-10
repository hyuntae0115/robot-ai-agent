import tempfile

import sounddevice as sd
import scipy.io.wavfile as wav
import whisper


SAMPLE_RATE = 16000
RECORD_SECONDS = 4

model = whisper.load_model("base")


def listen_voice():
    print("Listening...")

    audio = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        wav.write(temp_file.name, SAMPLE_RATE, audio)
        audio_path = temp_file.name

    result = model.transcribe(
        audio_path,
        language="ko"
    )

    text = result["text"].strip() # type: ignore
    print(f"Recognized: {text}")

    return text