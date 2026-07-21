import time
from collections import deque

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 16000

CHUNK_SECONDS = 0.1
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_SECONDS)

CALIBRATION_SECONDS = 1.0
SILENCE_DURATION = 1.5
START_TIMEOUT = 10.0
MAX_RECORD_SECONDS = 20.0
PRE_RECORD_SECONDS = 0.5
MIN_SPEECH_SECONDS = 0.5


def calculate_volume(audio_chunk: np.ndarray) -> float:
    audio_float = audio_chunk.astype(np.float32)

    return float(
        np.sqrt(np.mean(audio_float**2))
    )


def measure_noise_level(stream: sd.InputStream) -> float:
    noise_volumes = []

    calibration_chunks = int(
        CALIBRATION_SECONDS / CHUNK_SECONDS
    )

    print("주변 소음을 측정합니다. 잠시 조용히 해주세요.")

    for _ in range(calibration_chunks):
        audio_chunk, overflowed = stream.read(CHUNK_SIZE)

        if overflowed:
            print("Warning: audio input overflowed")

        volume = calculate_volume(audio_chunk)
        noise_volumes.append(volume)

    noise_level = float(np.mean(noise_volumes))

    threshold = max(
        noise_level * 2.0,
        200.0
    )

    print(f"Noise level: {noise_level:.1f}")
    print(f"Speech threshold: {threshold:.1f}")

    return threshold


def record_until_silence() -> np.ndarray | None:
    audio_chunks = []

    pre_record_chunk_count = int(
        PRE_RECORD_SECONDS / CHUNK_SECONDS
    )

    pre_record_buffer = deque(
        maxlen=pre_record_chunk_count
    )

    speech_started = False
    speech_start_time = None
    silence_start_time = None
    waiting_start_time = time.time()

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE
    ) as stream:
        threshold = measure_noise_level(stream)

        print("말씀하세요.")

        while True:
            audio_chunk, overflowed = stream.read(CHUNK_SIZE)

            if overflowed:
                print("Warning: audio input overflowed")

            audio_chunk = audio_chunk.copy()
            volume = calculate_volume(audio_chunk)
            current_time = time.time()

            if not speech_started:
                pre_record_buffer.append(audio_chunk)

                if volume >= threshold:
                    speech_started = True
                    speech_start_time = current_time

                    audio_chunks.extend(pre_record_buffer)
                    pre_record_buffer.clear()

                    print("음성이 감지되었습니다.")

                elif current_time - waiting_start_time >= START_TIMEOUT:
                    print("음성이 감지되지 않았습니다.")
                    return None

            else:
                audio_chunks.append(audio_chunk)

                if volume < threshold:
                    if silence_start_time is None:
                        silence_start_time = current_time

                    elif (
                        current_time - silence_start_time
                        >= SILENCE_DURATION
                    ):
                        print("말하기가 종료되었습니다.")
                        break

                else:
                    silence_start_time = None

                if (
                    speech_start_time is not None
                    and current_time - speech_start_time
                    >= MAX_RECORD_SECONDS
                ):
                    print("최대 녹음 시간에 도달했습니다.")
                    break

    if not audio_chunks:
        return None

    audio = np.concatenate(audio_chunks, axis=0)
    recorded_seconds = len(audio) / SAMPLE_RATE

    print(f"Recorded duration: {recorded_seconds:.2f} seconds")

    if recorded_seconds < MIN_SPEECH_SECONDS:
        print("녹음된 음성이 너무 짧습니다.")
        return None

    return audio