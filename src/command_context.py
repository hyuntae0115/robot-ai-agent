class CommandContext:

    REQUIRED_TARGET_FIELDS = (
        "x",
        "y",
        "z",
    )

    REQUIRED_MACHINE_FIELDS = (
        "material",
        "depth",
    )

    def __init__(self):
        self.pending_target = self._create_empty_target()
        self.pending_machine = self._create_empty_machine()

        self.applied_target = self._create_empty_target()
        self.applied_machine = self._create_empty_machine()

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
            "feed": None,
            "depth": None,
            "tool": None,
            "diameter": None,
        }

    def get_missing_fields(self):
        missing_fields = []

        for field in self.REQUIRED_TARGET_FIELDS:
            if self.pending_target.get(field) is None:
                missing_fields.append(
                    ("target", field)
                )

        for field in self.REQUIRED_MACHINE_FIELDS:
            if self.pending_machine.get(field) is None:
                missing_fields.append(
                    ("machine", field)
                )

        return missing_fields

    def get_first_missing_field(self):
        missing_fields = self.get_missing_fields()

        if not missing_fields:
            return None

        return missing_fields[0]

    def is_complete(self):
        return len(self.get_missing_fields()) == 0

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

    def clear_pending(self):
        self.pending_target = (
            self._create_empty_target()
        )

        self.pending_machine = (
            self._create_empty_machine()
        )

    def apply_and_clear(self):
        self.apply_pending()
        self.clear_pending()

    def clear(self):
        """기존 GUI의 command_context.clear() 호환용."""
        self.clear_pending()