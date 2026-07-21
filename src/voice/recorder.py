import time
from collections import deque
from collections.abc import Callable

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


StatusCallback = Callable[[str], None]


def send_status(
    status_callback: StatusCallback | None,
    message: str
) -> None:
    """
    상태 콜백이 전달된 경우 GUI 또는 콘솔에 상태 메시지를 보낸다.
    """
    if status_callback is not None:
        status_callback(message)


def calculate_volume(audio_chunk: np.ndarray) -> float:
    """
    오디오 청크의 RMS 음량을 계산한다.
    """
    audio_float = audio_chunk.astype(np.float32)

    return float(
        np.sqrt(np.mean(audio_float**2))
    )


def measure_noise_level(
    stream: sd.InputStream,
    status_callback: StatusCallback | None = None
) -> float:
    """
    주변 소음을 일정 시간 측정한 뒤
    음성 감지에 사용할 기준값을 계산한다.
    """
    send_status(
        status_callback,
        "주변 소음 측정 중입니다.\n"
        "측정이 끝날 때까지 잠시 조용히 해주세요."
    )

    print("주변 소음을 측정하는 중입니다.")

    noise_volumes: list[float] = []

    calibration_chunks = int(
        CALIBRATION_SECONDS / CHUNK_SECONDS
    )

    for _ in range(calibration_chunks):
        audio_chunk, overflowed = stream.read(CHUNK_SIZE)

        if overflowed:
            print("Warning: audio input overflowed")

        volume = calculate_volume(audio_chunk)
        noise_volumes.append(volume)

    if not noise_volumes:
        raise RuntimeError("주변 소음 측정에 실패했습니다.")

    noise_level = float(np.mean(noise_volumes))

    threshold = max(
        noise_level * 2.0,
        200.0
    )

    print(f"Noise level: {noise_level:.1f}")
    print(f"Speech threshold: {threshold:.1f}")

    send_status(
        status_callback,
        "주변 소음 측정이 끝났습니다.\n"
        "지금 말씀하세요."
    )

    return threshold


def record_until_silence(
    status_callback: StatusCallback | None = None
) -> np.ndarray | None:
    """
    사용자의 음성이 시작될 때까지 기다린 뒤,
    일정 시간 침묵이 이어지면 녹음을 종료한다.
    """
    audio_chunks: list[np.ndarray] = []

    pre_record_chunk_count = max(
        1,
        int(PRE_RECORD_SECONDS / CHUNK_SECONDS)
    )

    pre_record_buffer: deque[np.ndarray] = deque(
        maxlen=pre_record_chunk_count
    )

    speech_started = False
    speech_start_time: float | None = None
    silence_start_time: float | None = None

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SIZE
        ) as stream:
            threshold = measure_noise_level(
                stream,
                status_callback
            )

            waiting_start_time = time.time()

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

                        send_status(
                            status_callback,
                            "음성이 감지되었습니다.\n"
                            "계속 말씀하세요."
                        )

                    elif (
                        current_time - waiting_start_time
                        >= START_TIMEOUT
                    ):
                        print("음성이 감지되지 않았습니다.")

                        send_status(
                            status_callback,
                            "음성이 감지되지 않았습니다.\n"
                            "음성 입력 버튼을 다시 눌러주세요."
                        )

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

                            send_status(
                                status_callback,
                                "음성 입력이 끝났습니다.\n"
                                "인식을 준비하고 있습니다."
                            )

                            break

                    else:
                        silence_start_time = None

                    if (
                        speech_start_time is not None
                        and current_time - speech_start_time
                        >= MAX_RECORD_SECONDS
                    ):
                        print("최대 녹음 시간에 도달했습니다.")

                        send_status(
                            status_callback,
                            "최대 녹음 시간에 도달했습니다.\n"
                            "음성 입력을 종료합니다."
                        )

                        break

    except sd.PortAudioError as error:
        print(f"마이크 오류: {error}")

        send_status(
            status_callback,
            f"마이크 오류가 발생했습니다.\n{error}"
        )

        return None

    except Exception as error:
        print(f"음성 녹음 오류: {error}")

        send_status(
            status_callback,
            f"음성 녹음 중 오류가 발생했습니다.\n{error}"
        )

        return None

    if not audio_chunks:
        send_status(
            status_callback,
            "녹음된 음성이 없습니다."
        )

        return None

    audio = np.concatenate(
        audio_chunks,
        axis=0
    )

    recorded_seconds = len(audio) / SAMPLE_RATE

    print(
        f"Recorded duration: "
        f"{recorded_seconds:.2f} seconds"
    )

    if recorded_seconds < MIN_SPEECH_SECONDS:
        print("녹음된 음성이 너무 짧습니다.")

        send_status(
            status_callback,
            "녹음된 음성이 너무 짧습니다.\n"
            "다시 시도해주세요."
        )

        return None

    send_status(
        status_callback,
        "음성 녹음이 완료되었습니다."
    )

    return audio