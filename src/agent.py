import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras

from command import Command
from units import convert_distance_to_mm, convert_angle_to_deg
from typing import Any


# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 경로
ENV_PATH = BASE_DIR / ".env"

# Prompt 파일 경로
PROMPT_PATH = BASE_DIR / "prompts" / "ai_command_prompt.txt"

# 환경변수 로드
load_dotenv(dotenv_path=ENV_PATH)

cerebras_api_key = os.getenv("CEREBRAS_API_KEY")

if not cerebras_api_key:
    raise ValueError(
        f"CEREBRAS_API_KEY is not loaded. Check .env file path: {ENV_PATH}"
    )

os.environ["CEREBRAS_API_KEY"] = cerebras_api_key

# LLM 생성
llm = ChatCerebras(
    model="gpt-oss-120b",
    base_url="https://api.cerebras.ai/v1"
)


def json_to_command(item: dict) -> dict:
    command_name = item.get("command")

    try:
        if command_name == "rotate":
            axis = item["axis"]
            angle = float(item["angle"])
            unit = item["unit"]

            angle_deg = convert_angle_to_deg(angle, unit)

            return {
                "valid": True,
                "command":Command(
                    "rotate",
                    axis=axis,
                    angle=angle_deg
                )
            }
        
        if command_name == "machine":
            material = item.get("material")
            rpm = item.get("rpm")
            depth = item.get("depth")
            tool = item.get("tool")

            if rpm is not None:
                rpm = int(rpm)

            if depth is not None:
                depth = float(depth)

            return {
                "valid": True,
                "command": Command(
                    "machine",
                    material=material,
                    rpm=rpm,
                    depth=depth,
                    tool=tool
                )
            }
        
        if command_name == "status":
            return {
                "valid": True,
                "command": Command("status")
            }

        if command_name == "stop":
            return {
                "valid": True,
                "command": Command("stop")
            }

        return {
            "valid": False,
            "error": f"Unknown command: {command_name}"
        }

    except KeyError as error:
        return {
            "valid": False,
            "error": f"Missing field: {error}"
        }

    except ValueError as error:
        return {
            "valid": False,
            "error": str(error)
        }


def process(user_input: str):

    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        prompt = file.read()

    prompt = prompt.format(user_input=user_input)

    response = llm.invoke(prompt)
    raw_output = str(response.content).strip()

    print(f"LLM JSON Output:\n{raw_output}")

    try:
        data = json.loads(raw_output)

    except json.JSONDecodeError:
        return [{
            "valid": False,
            "error": f"Invalid JSON from LLM: {raw_output}"
        }], raw_output

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return [{
            "valid": False,
            "error": "LLM output must be a JSON object or array"
        }], raw_output

    parsed_commands = []

    for item in data:
        parsed_commands.append(json_to_command(item))

    return parsed_commands, raw_output