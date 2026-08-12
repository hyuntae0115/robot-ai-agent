import json
import socket


ISAAC_PC_IP = "220.149.217.38"
ISAAC_PC_PORT = 5000


def _send_request(message, timeout=5.0):
    with socket.create_connection(
        (ISAAC_PC_IP, ISAAC_PC_PORT),
        timeout=timeout,
    ) as connection:
        connection.sendall(
            (json.dumps(message) + "\n").encode("utf-8")
        )

        response_bytes = connection.recv(4096)

    if not response_bytes:
        raise ConnectionError("Isaac Sim 컴퓨터에서 응답이 없습니다.")

    response = json.loads(response_bytes.decode("utf-8").strip())
    if not response.get("success", False):
        raise RuntimeError(
            response.get("message", "Isaac Sim 명령 전송 실패")
        )

    return response


def send_drilling_command(request, timeout=5.0):
    if request.get("command") != "run_drilling":
        raise ValueError("command는 run_drilling이어야 합니다.")

    return _send_request(request, timeout=timeout)


def send_joint_command(joint_positions, timeout=5.0):
    if len(joint_positions) != 6:
        raise ValueError("HH020 관절각은 6개여야 합니다.")

    message = {
        "command": "joint",
        "joint_positions": [
            float(value) for value in joint_positions
        ],
    }

    return _send_request(message, timeout=timeout)