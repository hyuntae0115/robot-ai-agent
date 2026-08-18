class CommandContext:

    REQUIRED_TARGET_FIELDS = (
        "x",
        "y",
        "z",
    )

    REQUIRED_MACHINE_FIELDS = (
        "material",
        "depth",
        "diameter",
    )

    def __init__(self):
        # 사용자가 작성 중인 값
        self.pending_target = (
            self._create_empty_target()
        )
        self.pending_machine = (
            self._create_empty_machine()
        )

        # 1차 절삭조건 추천 결과
        self.recommendation = None

        # Isaac Sim 검증 결과
        self.simulation_result = None

        # 실제 적용된 값
        self.applied_target = (
            self._create_empty_target()
        )
        self.applied_machine = (
            self._create_empty_machine()
        )

        self.applied_recommendation = None
        self.applied_simulation_result = None

    @staticmethod
    def _create_empty_target():
        return {
            "x": None,
            "y": None,
            "z": None,
        }

    @staticmethod
    def _create_empty_machine():
        return {
            "process": None,
            "material": None,
            "rpm": None,

            # feed 단위는 항상 mm/rev
            "feed": None,

            "depth": None,
            "tool": None,
            "diameter": None,
        }

    def get_missing_fields(self):
        missing_fields = []

        for field in (
            self.REQUIRED_TARGET_FIELDS
        ):
            if (
                self.pending_target.get(field)
                is None
            ):
                missing_fields.append(
                    ("target", field)
                )

        for field in (
            self.REQUIRED_MACHINE_FIELDS
        ):
            if (
                self.pending_machine.get(field)
                is None
            ):
                missing_fields.append(
                    ("machine", field)
                )

        return missing_fields

    def get_first_missing_field(self):
        missing_fields = (
            self.get_missing_fields()
        )

        if not missing_fields:
            return None

        return missing_fields[0]

    def is_complete(self):
        return (
            len(self.get_missing_fields()) == 0
        )

    def has_recommendation(self):
        return self.recommendation is not None

    def has_valid_simulation(self):
        if self.simulation_result is None:
            return False

        if isinstance(
            self.simulation_result,
            dict,
        ):
            return bool(
                self.simulation_result.get(
                    "success",
                    False,
                )
            )

        return bool(
            getattr(
                self.simulation_result,
                "success",
                False,
            )
        )

    def invalidate_recommendation(self):
        """
        소재, 깊이 또는 직경이 변경됐을 때
        기존 1차 추천 결과를 삭제한다.
        """
        self.recommendation = None

        self.pending_machine["rpm"] = None
        self.pending_machine["feed"] = None

        # 추천 서비스에서 정한 공구도 초기화한다.
        self.pending_machine["tool"] = None

        # 추천 입력이 변경되면 기존 시뮬레이션도 무효다.
        self.simulation_result = None

    def invalidate_simulation(self):
        """
        좌표나 가공조건이 변경됐을 때
        기존 Isaac Sim 결과를 삭제한다.
        """
        self.simulation_result = None

    def set_recommendation(
        self,
        recommendation,
    ):
        """
        1차 추천 결과를 저장하고
        추천 RPM, Feed, 공구를 pending에 반영한다.
        """
        self.recommendation = recommendation

        if isinstance(recommendation, dict):
            rpm = recommendation.get("rpm")
            feed = recommendation.get(
                "feed_mm_rev"
            )
            tool = recommendation.get("tool")

        else:
            rpm = recommendation.rpm
            feed = recommendation.feed_mm_rev
            tool = recommendation.tool

        self.pending_machine["rpm"] = rpm
        self.pending_machine["feed"] = feed

        if tool is not None:
            self.pending_machine["tool"] = tool

        # 추천값이 새로 들어왔으므로
        # 이전 시뮬레이션 결과는 더 이상 유효하지 않다.
        self.simulation_result = None

    def set_simulation_result(
        self,
        simulation_result,
    ):
        self.simulation_result = (
            simulation_result
        )

    def apply_pending(self):
        if not self.is_complete():
            raise ValueError(
                "필수 작업정보가 입력되지 않았습니다."
            )

        self.applied_target = (
            self.pending_target.copy()
        )

        self.applied_machine = (
            self.pending_machine.copy()
        )

        self.applied_recommendation = (
            self.recommendation
        )

        self.applied_simulation_result = (
            self.simulation_result
        )

    def clear_pending(self):
        self.pending_target = (
            self._create_empty_target()
        )

        self.pending_machine = (
            self._create_empty_machine()
        )

        self.recommendation = None
        self.simulation_result = None

    def apply_and_clear(self):
        self.apply_pending()
        self.clear_pending()

    def clear(self):
        """
        기존 GUI의 command_context.clear()
        호출과 호환하기 위한 메서드.
        """
        self.clear_pending()