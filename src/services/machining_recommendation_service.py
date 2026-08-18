"""드릴링 RPM/Feed 초기 추천 서비스.

사용자가 RPM 또는 Feed를 직접 입력한 경우 그 값은 유지한다.
향후 학습 모델을 붙일 때 이 파일의 ``recommend_missing_conditions``만
동일한 입출력 형식으로 교체하면 된다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# 초경 드릴 기준의 보수적인 초기 절삭속도(m/min)
CUTTING_SPEED_M_MIN = {
    "aluminum": 120.0,
    "stainless_steel": 35.0,
    "carbon_steel": 60.0,
    "steel": 55.0,
    "titanium": 25.0,
    "pure_iron": 45.0,
}

MATERIAL_ALIASES = {
    "알루미늄": "aluminum",
    "알미늄": "aluminum",
    "aluminium": "aluminum",
    "a6061": "aluminum",
    "a7075": "aluminum",
    "스텐": "stainless_steel",
    "스테인리스": "stainless_steel",
    "스테인레스": "stainless_steel",
    "sus": "stainless_steel",
    "sus304": "stainless_steel",
    "sus316": "stainless_steel",
    "stainless steel": "stainless_steel",
    "탄소강": "carbon_steel",
    "연강": "carbon_steel",
    "carbon steel": "carbon_steel",
    "mild steel": "carbon_steel",
    "ss400": "carbon_steel",
    "s45c": "carbon_steel",
    "강철": "steel",
    "강재": "steel",
    "스틸": "steel",
    "철판": "steel",
    "티타늄": "titanium",
    "타이타늄": "titanium",
    "ti-6al-4v": "titanium",
    "ti64": "titanium",
    "순철": "pure_iron",
    "순수 철": "pure_iron",
    "pure iron": "pure_iron",
}

FEED_MATERIAL_FACTOR = {
    "aluminum": 1.15,
    "stainless_steel": 0.75,
    "carbon_steel": 1.0,
    "steel": 0.95,
    "titanium": 0.65,
    "pure_iron": 0.9,
}


@dataclass(frozen=True)
class RecommendationResult:
    rpm: int
    feed: float
    rpm_was_recommended: bool
    feed_was_recommended: bool
    assumptions: tuple[str, ...]

    @property
    def changed(self) -> bool:
        return self.rpm_was_recommended or self.feed_was_recommended

    def to_message(self) -> str:
        parts = ["가공조건 추천 결과"]
        if self.rpm_was_recommended:
            parts.append(f"RPM: {self.rpm} RPM")
        else:
            parts.append(f"RPM: {self.rpm} RPM (사용자 입력 유지)")
        if self.feed_was_recommended:
            parts.append(f"Feed: {self.feed:.3f} mm/rev")
        else:
            parts.append(f"Feed: {self.feed:.3f} mm/rev (사용자 입력 유지)")
        if self.assumptions:
            parts.append("가정: " + ", ".join(self.assumptions))
        parts.append("※ 초기 시뮬레이션용 기준값이며 실제 가공 전 검증이 필요합니다.")
        return "\n".join(parts)


def _normalize_material(value: object) -> str:
    text = str(value or "").strip().lower()
    return MATERIAL_ALIASES.get(text, text.replace("-", "_"))


def _base_feed_mm_rev(diameter_mm: float) -> float:
    if diameter_mm <= 3.0:
        return 0.05
    if diameter_mm <= 6.0:
        return 0.10
    if diameter_mm <= 10.0:
        return 0.16
    if diameter_mm <= 16.0:
        return 0.22
    return 0.28


def recommend_missing_conditions(machine: dict) -> RecommendationResult | None:
    """machine의 비어 있는 rpm/feed만 계산해 원본 dict에 저장한다."""
    if machine.get("material") is None:
        return None
    if machine.get("rpm") is not None and machine.get("feed") is not None:
        return None

    material = _normalize_material(machine["material"])
    assumptions: list[str] = []

    cutting_speed = CUTTING_SPEED_M_MIN.get(material)
    if cutting_speed is None:
        cutting_speed = 45.0
        assumptions.append("미등록 재질 절삭속도 45 m/min")

    raw_diameter = machine.get("diameter")
    if raw_diameter is None:
        diameter_mm = 10.0
        assumptions.append("공구 직경 10 mm")
    else:
        diameter_mm = float(raw_diameter)
        if diameter_mm <= 0:
            raise ValueError("공구 직경은 0보다 커야 합니다.")

    if machine.get("tool") is None:
        assumptions.append("초경 드릴")

    recommended_rpm = max(
        1,
        int(round((1000.0 * cutting_speed) / (math.pi * diameter_mm))),
    )
    recommended_feed = round(
        _base_feed_mm_rev(diameter_mm)
        * FEED_MATERIAL_FACTOR.get(material, 0.85),
        3,
    )

    rpm_missing = machine.get("rpm") is None
    feed_missing = machine.get("feed") is None
    if rpm_missing:
        machine["rpm"] = recommended_rpm
    if feed_missing:
        machine["feed"] = recommended_feed

    return RecommendationResult(
        rpm=int(machine["rpm"]),
        feed=float(machine["feed"]),
        rpm_was_recommended=rpm_missing,
        feed_was_recommended=feed_missing,
        assumptions=tuple(assumptions),
    )
