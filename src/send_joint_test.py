import json
import socket


ISAAC_PC_IP = "220.149.217.38"
PORT = 5000

command = {
    "command": "joint",
    "joint_positions": [
        0.0873,
        0.0781,
        -0.0141,
        0.0,
        0.0,
        0.0,
    ],
}

with socket.create_connection(
    (ISAAC_PC_IP, PORT),
    timeout=5.0,
) as connection:
    connection.sendall(
        (json.dumps(command) + "\n").encode("utf-8")
    )

    response = connection.recv(4096).decode("utf-8")
    print("Ubuntu 응답:", response)