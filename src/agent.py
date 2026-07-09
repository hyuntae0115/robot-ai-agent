import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

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


openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        f"OPENAI_API_KEY is not loaded. Check .env file path: {ENV_PATH}"
    )

client = OpenAI(api_key=openai_api_key)

def json_to_command(item: dict) -> dict:
    command_name = item.get("command")

    try:
        if command_name == "move":
            direction = item["direction"]
            distance = float(item["distance"])
            unit = item["unit"]

            distance_mm = convert_distance_to_mm(distance, unit)

            return {
                "valid": True,
                "command": Command(
                    "move",
                    direction=direction,
                    distance=distance_mm
                )
            }

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
            pose = item.get("pose")
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
                    pose=pose,
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

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )   

    raw_output = response.output_text.strip()

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