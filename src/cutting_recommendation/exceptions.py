class CuttingRecommendationError(Exception):
    """절삭조건 추천 과정의 기본 오류."""


class InvalidCuttingInputError(
    CuttingRecommendationError
):
    """직경, 깊이 등의 입력값이 잘못된 경우."""


class UnsupportedMaterialError(
    CuttingRecommendationError
):
    """추천 데이터가 없는 소재인 경우."""


class CuttingDataNotFoundError(
    CuttingRecommendationError
):
    """입력 조합과 일치하는 절삭 데이터가 없는 경우."""


class CuttingDataFormatError(
    CuttingRecommendationError
):
    """Excel 형식이나 데이터에 문제가 있는 경우."""