from __future__ import annotations

import re
from dataclasses import dataclass

from .exceptions import UnsupportedMaterialError


@dataclass(frozen=True)
class MaterialDefinition:
    canonical_name: str
    display_name: str
    excel_filename: str


MATERIAL_DEFINITIONS = {
    # Aluminum
    "aluminum": MaterialDefinition(
        canonical_name="aluminum",
        display_name="Al6061",
        excel_filename="Al6061.xlsx",
    ),
    "al6061": MaterialDefinition(
        canonical_name="aluminum",
        display_name="Al6061",
        excel_filename="Al6061.xlsx",
    ),
    "6061": MaterialDefinition(
        canonical_name="aluminum",
        display_name="Al6061",
        excel_filename="Al6061.xlsx",
    ),

    # Stainless steel
    "stainlesssteel": MaterialDefinition(
        canonical_name="stainless_steel",
        display_name="SUS316",
        excel_filename="SUS316.xlsx",
    ),
    "sus316": MaterialDefinition(
        canonical_name="stainless_steel",
        display_name="SUS316",
        excel_filename="SUS316.xlsx",
    ),
    "sts316": MaterialDefinition(
        canonical_name="stainless_steel",
        display_name="SUS316",
        excel_filename="SUS316.xlsx",
    ),

    # Titanium
    "titanium": MaterialDefinition(
        canonical_name="titanium",
        display_name="Ti6Al4V",
        excel_filename="Ti6Al4V.xlsx",
    ),
    "ti6al4v": MaterialDefinition(
        canonical_name="titanium",
        display_name="Ti6Al4V",
        excel_filename="Ti6Al4V.xlsx",
    ),
    "ti64": MaterialDefinition(
        canonical_name="titanium",
        display_name="Ti6Al4V",
        excel_filename="Ti6Al4V.xlsx",
    ),

    # Cast iron
    "iron": MaterialDefinition(
        canonical_name="iron",
        display_name="Cast Iron FC250",
        excel_filename="Cast_Iron_FC250.xlsx",
    ),
    "castiron": MaterialDefinition(
        canonical_name="iron",
        display_name="Cast Iron FC250",
        excel_filename="Cast_Iron_FC250.xlsx",
    ),
    "castironfc250": MaterialDefinition(
        canonical_name="iron",
        display_name="Cast Iron FC250",
        excel_filename="Cast_Iron_FC250.xlsx",
    ),
    "fc250": MaterialDefinition(
        canonical_name="iron",
        display_name="Cast Iron FC250",
        excel_filename="Cast_Iron_FC250.xlsx",
    ),
}


def normalize_material_name(
    material: object
) -> str:
    return re.sub(
        r"[^0-9a-z]+",
        "",
        str(material).lower(),
    )


def map_material(
    material: str
) -> MaterialDefinition:
    normalized = normalize_material_name(
        material
    )

    definition = MATERIAL_DEFINITIONS.get(
        normalized
    )

    if definition is None:
        supported = (
            "aluminum, stainless_steel, "
            "titanium, iron"
        )

        raise UnsupportedMaterialError(
            "추천 데이터가 없는 소재입니다: "
            f"{material!r}\n"
            f"현재 지원 소재: {supported}"
        )

    return definition