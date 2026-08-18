from __future__ import annotations

from .exceptions import (
    InvalidCuttingInputError,
)
from .excel_repository import (
    CuttingDataRepository,
)
from .material_mapper import map_material
from .models import (
    CuttingRecommendation,
    CuttingRequest,
)


class CuttingRecommendationService:

    def __init__(
        self,
        repository: (
            CuttingDataRepository | None
        ) = None,
    ):
        self.repository = (
            repository
            or CuttingDataRepository()
        )

    @staticmethod
    def _validate_request(
        request: CuttingRequest,
    ) -> None:
        if not request.material.strip():
            raise InvalidCuttingInputError(
                "material이 입력되지 않았습니다."
            )

        if request.diameter_mm <= 0:
            raise InvalidCuttingInputError(
                "diameter_mm는 "
                "0보다 커야 합니다."
            )

        if request.depth_mm <= 0:
            raise InvalidCuttingInputError(
                "depth_mm는 "
                "0보다 커야 합니다."
            )

    def recommend(
        self,
        request: CuttingRequest,
    ) -> CuttingRecommendation:
        self._validate_request(request)

        material_definition = (
            map_material(request.material)
        )

        result = self.repository.find_exact(
            material=material_definition,
            diameter_mm=request.diameter_mm,
            depth_mm=request.depth_mm,
        )

        return CuttingRecommendation(
            material=(
                material_definition
                .canonical_name
            ),
            diameter_mm=(
                result["diameter_mm"]
            ),
            depth_mm=result["depth_mm"],
            vc_m_min=result["vc_m_min"],
            rpm=result["rpm"],
            feed_mm_rev=(
                result["feed_mm_rev"]
            ),
            tool=result["tool"],
            source_file=(
                result["source_file"]
            ),
            source_row=(
                result["source_row"]
            ),
        )