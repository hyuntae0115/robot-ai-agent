from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from cutting_recommendation.models import (
    CuttingRecommendation,
)


@dataclass(frozen=True)
class SimulationResult:
    success: bool
    collision: bool
    singularity: bool

    joint_angles: list[float]
    message: str

    request: dict[str, Any]
    raw_response: dict[str, Any]


class SimulationService:

    def __init__(
        self,
        sender: (
            Callable[
                [dict[str, Any]],
                dict[str, Any],
            ]
            | None
        ) = None,
        command_name: str = "run_drilling",
    ):
        if sender is None:
            from simulation.isaac_client import (
                send_drilling_command,
            )

            sender = send_drilling_command

        self.sender = sender
        self.command_name = command_name

    def validate(
        self,
        target: dict[str, Any],
        machine: dict[str, Any],
        recommendation: (
            CuttingRecommendation
        ),
    ) -> SimulationResult:
        for axis in ("x", "y", "z"):
            if target.get(axis) is None:
                raise ValueError(
                    f"목표 위치 {axis} "
                    "값이 없습니다."
                )

        material = machine.get("material")

        if material is None:
            raise ValueError(
                "가공 소재가 입력되지 않았습니다."
            )

        request = {
            "command": self.command_name,
            "material": material,

            # Robot AI Agent 내부 좌표: mm
            # Isaac Sim 전송 좌표: m
            "x": float(target["x"]) / 1000.0,
            "y": float(target["y"]) / 1000.0,
            "z": float(target["z"]) / 1000.0,

            "diameter_mm": (
                recommendation.diameter_mm
            ),
            "depth_mm": (
                recommendation.depth_mm
            ),
            "vc_m_min": (
                recommendation.vc_m_min
            ),
            "rpm": recommendation.rpm,
            "feed_mm_rev": (
                recommendation.feed_mm_rev
            ),
            "tool": recommendation.tool,
        }

        response = self.sender(request)

        if not isinstance(response, dict):
            raise TypeError(
                "Isaac Sim 응답은 "
                "dict여야 합니다."
            )

        collision = bool(
            response.get(
                "collision",
                False,
            )
        )

        singularity = bool(
            response.get(
                "singularity",
                False,
            )
        )

        response_success = bool(
            response.get(
                "success",
                response.get("ok", False),
            )
        )

        success = (
            response_success
            and not collision
            and not singularity
        )

        joint_angles_value = response.get(
            "joint_angles",
            response.get("joints", []),
        )

        if joint_angles_value is None:
            joint_angles_value = []

        if not isinstance(
            joint_angles_value,
            (list, tuple),
        ):
            raise TypeError(
                "joint_angles는 "
                "list여야 합니다."
            )

        joint_angles = [
            float(value)
            for value in joint_angles_value
        ]

        return SimulationResult(
            success=success,
            collision=collision,
            singularity=singularity,
            joint_angles=joint_angles,
            message=str(
                response.get("message", "")
            ),
            request=request,
            raw_response=response,
        )