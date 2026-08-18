from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CuttingRequest:
    material: str
    diameter_mm: float
    depth_mm: float


@dataclass(frozen=True)
class CuttingRecommendation:
    material: str
    diameter_mm: float
    depth_mm: float

    vc_m_min: float
    rpm: int
    feed_mm_rev: float

    tool: str | None

    source_file: str
    source_row: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)