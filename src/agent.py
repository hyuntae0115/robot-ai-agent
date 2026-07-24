import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from command import Command
from units import convert_distance_to_mm


# 프로젝트 루트 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 경로
ENV_PATH = BASE_DIR / ".env"

# Prompt 파일 경로
PROMPT_PATH = (
    BASE_DIR
    / "prompts"
    / "ai_command_prompt.txt"
)

# 환경변수 로드
load_dotenv(dotenv_path=ENV_PATH)


openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY is not loaded. "
        f"Check .env file path: {ENV_PATH}"
    )


client = OpenAI(
    api_key=openai_api_key
)


def json_to_command(item: dict) -> dict:
    command_name = item.get("command")

    try:
        if command_name == "target":
            position = item["position"]
            distance_unit = item["distance_unit"]

            converted_position = {
                "x": convert_distance_to_mm(
                    position["x"],
                    distance_unit
                ),
                "y": convert_distance_to_mm(
                    position["y"],
                    distance_unit
                ),
                "z": convert_distance_to_mm(
                    position["z"],
                    distance_unit
                )
            }

            return {
                "valid": True,
                "command": Command(
                    "target",
                    position=converted_position
                )
            }

        if command_name == "machine":
            machining_process = item.get("process")
            material = item.get("material")
            rpm = item.get("rpm")
            depth = item.get("depth")
            tool = item.get("tool")
            diameter = item.get("diameter")

            if rpm is not None:
                rpm = int(rpm)

                if rpm <= 0:
                    return {
                        "valid": False,
                        "error": (
                            "RPM must be greater than 0."
                        )
                    }

            if depth is not None:
                depth = float(depth)

                if depth < 0:
                    return {
                        "valid": False,
                        "error": (
                            "Depth cannot be negative."
                        )
                    }

            if diameter is not None:
                diameter = float(diameter)

                if diameter <= 0:
                    return {
                        "valid": False,
                        "error": (
                            "Diameter must be greater than 0."
                        )
                    }

            return {
                "valid": True,
                "command": Command(
                    "machine",
                    process=machining_process,
                    material=material,
                    rpm=rpm,
                    depth=depth,
                    tool=tool,
                    diameter=diameter
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
            "error": (
                f"Unknown command: {command_name}"
            )
        }

    except KeyError as error:
        return {
            "valid": False,
            "error": f"Missing field: {error}"
        }

    except (TypeError, ValueError) as error:
        return {
            "valid": False,
            "error": str(error)
        }


def process(
    user_input: str,
    expected_field: tuple[str, str] | None = None
):
    with open(
        PROMPT_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        prompt = file.read()

    prompt = prompt.replace(
        "{user_input}",
        user_input
    )

    if expected_field is not None:
        command_name, field = expected_field

        clarification_instruction = f"""

Clarification answer context:

* The program previously asked the user for the missing
  "{field}" field of the "{command_name}" command.

* If the current user input contains only a bare value,
  interpret that value as the requested "{field}" field.

* A bare value means an answer such as:
  "3", "3000", "5mm", "알루미늄", or "엔드밀".

* If the user explicitly names a field, coordinate,
  machining process, material, tool, or another command,
  extract every explicitly provided value.

* Do not discard additional information merely because
  the program previously asked for one missing field.

* Explicit expressions in the current user input take priority
  over the previously expected field.

* Return every target and machine command explicitly indicated
  by the current user input.

* Fields that are not provided or inferable must be null.
"""

        if command_name == "target":
            clarification_instruction += f"""

* If the input is only a bare numeric value,
  store it in position["{field}"].

* Example:
  If the expected field is "y" and the user answers only "3",
  return a target command with x as null, y as 3, and z as null.

* However, if the user says "x는 500에서 밀링해줘",
  extract both:
  - a target command containing x = 500
  - a machine command containing process = "milling"

* Do not force an explicitly named coordinate into
  position["{field}"].
"""

        elif command_name == "machine":
            clarification_instruction += f"""

* If the input is only a bare value,
  interpret it as the machine field "{field}".

* If the input explicitly provides other machining values
  or target coordinates, extract those values as well.

* Always include every required machine key in a machine command.
"""
            
        prompt += clarification_instruction

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    raw_output = response.output_text.strip()

    print(
        "LLM JSON Output:\n"
        f"{raw_output}"
    )

    try:
        data = json.loads(raw_output)

    except json.JSONDecodeError:
        return [
            {
                "valid": False,
                "error": (
                    "Invalid JSON from LLM: "
                    f"{raw_output}"
                )
            }
        ], raw_output

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return [
            {
                "valid": False,
                "error": (
                    "LLM output must be "
                    "a JSON object or array"
                )
            }
        ], raw_output

    parsed_commands = []

    for item in data:
        if not isinstance(item, dict):
            parsed_commands.append(
                {
                    "valid": False,
                    "error": (
                        "Each command must be "
                        "a JSON object."
                    )
                }
            )
            continue

        parsed_commands.append(
            json_to_command(item)
        )

    return parsed_commands, raw_output