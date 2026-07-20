import math


def convert_distance_to_mm(
    value: int | float | None,
    unit: str
) -> int | float | None:
    if value is None:
        return None

    if unit == "mm":
        return value

    if unit == "cm":
        return value * 10

    if unit == "m":
        return value * 1000

    raise ValueError(f"Unsupported distance unit: {unit}")


def convert_angle_to_deg(value, unit):
    unit = unit.lower()

    if unit in ["deg", "degree", "degrees"]:
        return value

    if unit in ["rad", "radian", "radians"]:
        return math.degrees(value)

    raise ValueError(f"Unsupported angle unit: {unit}")

def normalize_angle(angle):
    while angle < 0:
        angle += 360

    while angle >= 360:
        angle -= 360

    return angle