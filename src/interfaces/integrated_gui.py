"""PySide6 기반 Robot AI Agent 통합 GUI 1단계.

현재 연결된 기능
-----------------
* 자연어 명령 분석: controller.handle_user_input
* Pending / Applied 작업정보 표시
* 작업 실행: controller.execute_pending_command
* Isaac Sim TCP/JSON 전송: isaac_client.send_drilling_command

다음 단계에서 연결할 영역
-------------------------
* Isaac Sim 실시간 영상 스트림
* 작업공간 카메라 스트림
* 힘/토크 및 열화상 센서 스트림
"""

from __future__ import annotations

import html
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from controller import execute_pending_command, handle_user_input
from simulation.isaac_client import send_drilling_command


COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "surface_alt": "#EAF0F8",
    "border": "#D5DFEC",
    "primary": "#3478F6",
    "primary_hover": "#2466DC",
    "success": "#16895A",
    "danger": "#CC3D42",
    "warning": "#D99000",
    "text": "#172033",
    "muted": "#68758A",
}


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class FunctionWorker(QRunnable):
    """GUI를 멈추지 않고 일반 Python 함수를 실행한다."""

    def __init__(self, function: Callable[..., Any], *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as error:  # GUI에 사람이 읽을 수 있는 오류 전달
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()


class Panel(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        # QWidget.layout() 메서드와 이름이 충돌하지 않도록 별도 이름 사용
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(18, 16, 18, 16)
        self.content_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")
        self.content_layout.addWidget(title_label)


class VideoPanel(Panel):
    """영상 수신기를 붙이기 전 사용하는 표시 영역."""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(title, parent)

        self.video_label = QLabel(description)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumHeight(180)
        self.video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.video_label.setObjectName("videoPlaceholder")
        self.content_layout.addWidget(self.video_label, 1)

        self.status_label = QLabel("● 스트림 연결 대기")
        self.status_label.setObjectName("mutedLabel")
        self.content_layout.addWidget(self.status_label)

    def set_connection_state(self, connected: bool, message: str):
        color = COLORS["success"] if connected else COLORS["danger"]
        self.status_label.setText(f"● {message}")
        self.status_label.setStyleSheet(f"color: {color};")


class ChatPanel(Panel):
    command_submitted = Signal(str)
    execute_requested = Signal()
    clear_requested = Signal()

    AGENT_LABELS = {
        "user": ("사용자", "#3478F6", "#FFFFFF", None),
        "command": (
            "음성 명령 Agent",
            "#EEF3FF",
            "#244E86",
            "voice_command_agent.png",
        ),
        "validation": (
            "안전 검증 Agent",
            "#FFF1E9",
            "#98420D",
            "vision_safety_agent.png",
        ),
        "prediction": (
            "공정 모니터링 Agent",
            "#ECF8F2",
            "#166B4A",
            "process_monitoring_agent.png",
        ),
        "execution": (
            "로봇 동작 Agent",
            "#F3EEFF",
            "#5E3E9D",
            "robot_action_agent.png",
        ),
        "system": ("Robot AI Agent", "#EEF3F9", "#334155", None),
    }

    ICON_DIRECTORIES = (
        Path(__file__).resolve().parent / "assets" / "agent_icons",
        Path(__file__).resolve().parent.parent / "assets" / "agent_icons",
        Path.cwd() / "assets" / "agent_icons",
    )

    def __init__(self, parent=None):
        super().__init__("명령 및 Agent 대화", parent)

        # QWidget.scroll() 계열 이름과 Pylance가 혼동하지 않도록 명확히 명명
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(2, 2, 2, 2)
        self.message_layout.setSpacing(8)
        self.message_layout.addStretch(1)
        self.chat_scroll_area.setWidget(self.message_container)
        self.content_layout.addWidget(self.chat_scroll_area, 1)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText(
            "예: 알루미늄을 x 1123, y 0, z 1000에서 깊이 4 mm로 드릴링해줘"
        )
        self.entry.returnPressed.connect(self.submit)
        self.content_layout.addWidget(self.entry)

        button_row = QHBoxLayout()
        self.analyze_button = QPushButton("명령 분석")
        self.analyze_button.setObjectName("primaryButton")
        self.analyze_button.clicked.connect(self.submit)

        self.voice_button = QPushButton("음성 인식")
        self.voice_button.setToolTip("2단계에서 기존 voice 모듈을 연결합니다.")

        self.clear_button = QPushButton("입력 취소")
        self.clear_button.clicked.connect(self.clear_requested.emit)

        self.execute_button = QPushButton("작업 실행")
        self.execute_button.setObjectName("successButton")
        self.execute_button.setEnabled(False)
        self.execute_button.clicked.connect(self.execute_requested.emit)

        for button in (
            self.analyze_button,
            self.voice_button,
            self.clear_button,
            self.execute_button,
        ):
            button_row.addWidget(button)
        self.content_layout.addLayout(button_row)

    def submit(self):
        text = self.entry.text().strip()
        if not text:
            return
        self.entry.clear()
        self.command_submitted.emit(text)

    def set_busy(self, busy: bool):
        self.analyze_button.setEnabled(not busy)
        self.entry.setEnabled(not busy)

    @classmethod
    def _find_icon(cls, filename: str | None) -> Path | None:
        if not filename:
            return None

        for directory in cls.ICON_DIRECTORIES:
            icon_path = directory / filename
            if icon_path.exists():
                return icon_path

        return None

    def add_message(self, role: str, text: str):
        name, background, foreground, icon_filename = self.AGENT_LABELS.get(
            role,
            self.AGENT_LABELS["system"],
        )

        bubble = QLabel(
            f"<b>{html.escape(name)}</b><br>"
            f"{html.escape(str(text)).replace(chr(10), '<br>')}"
        )
        bubble.setWordWrap(True)
        bubble.setTextFormat(Qt.TextFormat.RichText)
        bubble.setMaximumWidth(470)
        bubble.setStyleSheet(
            f"background: {background}; color: {foreground};"
            "border-radius: 12px; padding: 11px;"
        )

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        if role == "user":
            row_layout.addStretch(1)
            row_layout.addWidget(bubble)
        else:
            icon_path = self._find_icon(icon_filename)
            if icon_path is not None:
                avatar = QLabel()
                avatar.setFixedSize(58, 58)
                avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
                avatar.setObjectName("agentAvatar")

                pixmap = QPixmap(str(icon_path))
                avatar.setPixmap(
                    pixmap.scaled(
                        52,
                        52,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                avatar.setToolTip(name)
                row_layout.addWidget(
                    avatar,
                    0,
                    Qt.AlignmentFlag.AlignTop,
                )

            row_layout.addWidget(bubble)
            row_layout.addStretch(1)

        self.message_layout.insertWidget(
            self.message_layout.count() - 1,
            row,
        )
        QApplication.processEvents()
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )


@dataclass(frozen=True)
class StatusField:
    key: str
    label: str
    unit: str = ""


STATUS_FIELDS = (
    StatusField("x", "X 위치", "m"),
    StatusField("y", "Y 위치", "m"),
    StatusField("z", "Z 위치", "m"),
    StatusField("material", "재질"),
    StatusField("process", "공정"),
    StatusField("tool", "공구"),
    StatusField("diameter", "직경", "mm"),
    StatusField("depth", "깊이", "mm"),
    StatusField("rpm", "회전속도", "RPM"),
    StatusField("feed", "이송량", "mm/rev"),
)


class JobStatusPanel(Panel):
    def __init__(self, parent=None):
        super().__init__("작업 실행 직전 대기값", parent)
        self.badge = QLabel("입력 대기")
        self.badge.setObjectName("warningLabel")
        self.content_layout.addWidget(self.badge)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(5)
        self.values: dict[str, QLabel] = {}

        for row, field in enumerate(STATUS_FIELDS):
            name = QLabel(field.label)
            name.setObjectName("mutedLabel")
            value = QLabel("—")
            value.setAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )
            value.setObjectName("valueLabel")
            grid.addWidget(name, row, 0)
            grid.addWidget(value, row, 1)
            self.values[field.key] = value

        self.content_layout.addLayout(grid)
        self.content_layout.addStretch(1)

    @staticmethod
    def _position(value):
        return "—" if value is None else f"{float(value) / 1000.0:.3f} m"

    @staticmethod
    def _value(value, unit=""):
        if value is None:
            return "—"
        return f"{value} {unit}".strip()

    def update_values(self, target: dict, machine: dict, missing_count: int):
        data = {
            "x": self._position(target.get("x")),
            "y": self._position(target.get("y")),
            "z": self._position(target.get("z")),
            "material": self._value(machine.get("material")),
            "process": self._value(machine.get("process")),
            "tool": self._value(machine.get("tool")),
            "diameter": self._value(machine.get("diameter"), "mm"),
            "depth": self._value(machine.get("depth"), "mm"),
            "rpm": self._value(machine.get("rpm"), "RPM"),
            "feed": self._value(machine.get("feed"), "mm/rev"),
        }
        for key, value in data.items():
            self.values[key].setText(value)

        if missing_count:
            self.badge.setText(f"필수값 {missing_count}개 입력 필요")
            self.badge.setStyleSheet(f"color: {COLORS['warning']};")
        else:
            self.badge.setText("실행 준비 완료")
            self.badge.setStyleSheet(f"color: {COLORS['success']};")


class SensorPanel(Panel):
    def __init__(self, parent=None):
        super().__init__("힘·토크 센서 및 열화상 온도", parent)

        grid = QGridLayout()
        fields = (
            ("Fx", "— N"), ("Fy", "— N"), ("Fz", "— N"),
            ("Tx", "— N·m"), ("Ty", "— N·m"), ("Tz", "— N·m"),
            ("최고 온도", "— °C"), ("평균 온도", "— °C"),
        )
        self.values = {}
        for index, (name, initial) in enumerate(fields):
            row, column = divmod(index, 4)
            item = QFrame()
            item.setObjectName("sensorItem")
            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            label = QLabel(name)
            label.setObjectName("mutedLabel")
            value = QLabel(initial)
            value.setObjectName("sensorValue")
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            grid.addWidget(item, row, column)
            self.values[name] = value
        self.content_layout.addLayout(grid)


class IntegratedRobotGUI(QMainWindow):
    def __init__(self, robot_state, command_context):
        super().__init__()
        self.robot_state = robot_state
        self.command_context = command_context
        self.thread_pool = QThreadPool.globalInstance()

        self.setWindowTitle("Robot AI Agent Integrated Control")
        self.resize(1600, 920)
        self.setMinimumSize(1280, 760)
        self._build_ui()
        self._apply_style()
        self.update_pending_panel()

        self.chat.add_message(
            "system",
            "통합 제어 GUI가 준비되었습니다. 자연어로 작업을 입력해주세요.",
        )

    def _build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(20, 16, 20, 16)
        root_layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Robot AI Agent · Integrated Control")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch(1)
        self.connection_label = QLabel("● Isaac Sim 대기")
        self.connection_label.setObjectName("warningLabel")
        header.addWidget(self.connection_label)
        root_layout.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.chat = ChatPanel()
        self.chat.setMinimumWidth(390)
        self.chat.command_submitted.connect(self.analyze_command)
        self.chat.execute_requested.connect(self.execute_job)
        self.chat.clear_requested.connect(self.clear_pending)
        splitter.addWidget(self.chat)

        right = QWidget()
        right_grid = QGridLayout(right)
        right_grid.setContentsMargins(0, 0, 0, 0)
        right_grid.setSpacing(12)
        right_grid.setColumnStretch(0, 2)
        right_grid.setColumnStretch(1, 4)
        right_grid.setColumnStretch(2, 2)
        right_grid.setRowStretch(0, 3)
        right_grid.setRowStretch(1, 2)

        self.pending_panel = JobStatusPanel()
        self.isaac_panel = VideoPanel(
            "Isaac Sim 실시간 화면",
            "Isaac Sim 영상 스트림\n연결 예정",
        )
        self.sensor_panel = SensorPanel()
        self.camera_panel = VideoPanel(
            "작업공간 카메라",
            "작업공간 카메라 스트림\n연결 예정",
        )

        right_grid.addWidget(self.pending_panel, 0, 0)
        right_grid.addWidget(self.isaac_panel, 0, 1, 1, 2)
        right_grid.addWidget(self.sensor_panel, 1, 0, 1, 2)
        right_grid.addWidget(self.camera_panel, 1, 2)

        splitter.addWidget(right)
        splitter.setSizes([430, 1120])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root_layout.addWidget(splitter, 1)

        self.status_label = QLabel("대기 중")
        self.status_label.setObjectName("mutedLabel")
        root_layout.addWidget(self.status_label)

        self.setCentralWidget(root)

    def _apply_style(self):
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            f"""
            QMainWindow, QWidget {{
                background: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QFrame#panel {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 14px;
            }}
            QLabel#pageTitle {{
                font-size: 24px;
                font-weight: 700;
                color: {COLORS['text']};
            }}
            QLabel#panelTitle {{
                font-size: 16px;
                font-weight: 700;
                color: {COLORS['text']};
            }}
            QLabel#mutedLabel {{ color: {COLORS['muted']}; }}
            QLabel#warningLabel {{ color: {COLORS['warning']}; font-weight: 600; }}
            QLabel#valueLabel {{ font-family: Consolas; font-weight: 600; }}
            QLabel#videoPlaceholder {{
                background: #E7EDF5;
                color: {COLORS['muted']};
                border: 1px dashed #AAB8CA;
                border-radius: 10px;
                font-size: 18px;
            }}
            QFrame#sensorItem {{
                background: {COLORS['surface_alt']};
                border: none;
                border-radius: 9px;
            }}
            QLabel#sensorValue {{ font-size: 17px; font-weight: 700; }}
            QLabel#agentAvatar {{
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background: {COLORS['surface_alt']};
                border: 1px solid {COLORS['border']};
                border-radius: 9px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton {{
                background: {COLORS['surface_alt']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 9px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #DCE6F3; }}
            QPushButton:disabled {{ color: #9AA6B6; background: #EDF1F6; }}
            QPushButton#primaryButton {{
                color: white;
                background: {COLORS['primary']};
                border: none;
            }}
            QPushButton#primaryButton:hover {{ background: {COLORS['primary_hover']}; }}
            QPushButton#successButton {{
                color: white;
                background: {COLORS['success']};
                border: none;
            }}
            QScrollArea {{ background: transparent; }}
            QSplitter::handle {{ background: transparent; width: 8px; }}
            """
        )

    def update_pending_panel(self):
        missing = self.command_context.get_missing_fields()
        self.pending_panel.update_values(
            self.command_context.pending_target,
            self.command_context.pending_machine,
            len(missing),
        )
        self.chat.execute_button.setEnabled(not missing)

    @Slot(str)
    def analyze_command(self, user_input: str):
        self.chat.add_message("user", user_input)
        self.chat.set_busy(True)
        self.status_label.setText("명령 분석 중")

        worker = FunctionWorker(
            handle_user_input,
            user_input,
            self.robot_state,
            self.command_context,
        )
        worker.signals.result.connect(self._analysis_finished)
        worker.signals.error.connect(self._analysis_failed)
        worker.signals.finished.connect(lambda: self.chat.set_busy(False))
        self.thread_pool.start(worker)

    @Slot(object)
    def _analysis_finished(self, payload):
        results, raw_output = payload
        if results:
            for result in results:
                result_text = str(result)
                if "가공조건 추천 결과" in result_text:
                    role = "prediction"
                elif "입력" in result_text:
                    role = "validation"
                else:
                    role = "command"
                self.chat.add_message(role, result_text)
        if raw_output:
            self.chat.add_message(
                "system",
                "LLM JSON\n" + str(raw_output),
            )
        self.update_pending_panel()
        self.status_label.setText("명령 분석 완료")

    @Slot(str)
    def _analysis_failed(self, message: str):
        self.chat.add_message("system", f"명령 처리 오류: {message}")
        self.status_label.setText("명령 분석 실패")

    def clear_pending(self):
        self.command_context.clear_pending()
        self.update_pending_panel()
        self.chat.add_message("system", "작성 중인 작업을 취소했습니다.")

    def _execute_and_send(self):
        target = dict(self.command_context.pending_target)
        machine = dict(self.command_context.pending_machine)

        local_results = execute_pending_command(
            self.robot_state,
            self.command_context,
        )

        request = {
            "command": "run_drilling",
            "material": machine["material"],
            "x": float(target["x"]) / 1000.0,
            "y": float(target["y"]) / 1000.0,
            "z": float(target["z"]) / 1000.0,
            "depth_mm": float(machine["depth"]),
        }
        if machine.get("rpm") is not None:
            request["rpm"] = int(machine["rpm"])
        if machine.get("feed") is not None:
            request["feed_mm_rev"] = float(machine["feed"])

        response = send_drilling_command(request)
        return {
            "local_results": local_results,
            "request": request,
            "response": response,
        }

    def execute_job(self):
        missing = self.command_context.get_missing_fields()
        if missing:
            fields = ", ".join(field for _, field in missing)
            self.chat.add_message(
                "validation",
                f"필수 작업정보가 부족합니다: {fields}",
            )
            return

        self.chat.execute_button.setEnabled(False)
        self.connection_label.setText("● Isaac Sim 전송 중")
        self.status_label.setText("작업 실행 중")

        worker = FunctionWorker(self._execute_and_send)
        worker.signals.result.connect(self._execution_finished)
        worker.signals.error.connect(self._execution_failed)
        self.thread_pool.start(worker)

    @Slot(object)
    def _execution_finished(self, payload):
        for result in payload["local_results"]:
            self.chat.add_message("execution", str(result))
        self.chat.add_message(
            "execution",
            "Isaac Sim 명령 전송 성공\n"
            + json.dumps(payload["request"], ensure_ascii=False),
        )
        self.connection_label.setText("● Isaac Sim 연결됨")
        self.connection_label.setStyleSheet(f"color: {COLORS['success']};")
        self.status_label.setText("작업 실행 완료")
        self.update_pending_panel()

    @Slot(str)
    def _execution_failed(self, message: str):
        self.chat.add_message(
            "execution",
            f"Isaac Sim 명령 전송 실패: {message}",
        )
        self.connection_label.setText("● Isaac Sim 연결 실패")
        self.connection_label.setStyleSheet(f"color: {COLORS['danger']};")
        self.status_label.setText("작업 실행 실패")
        self.update_pending_panel()


def run_integrated_gui(robot_state, command_context):
    app = QApplication.instance() or QApplication(sys.argv)
    window = IntegratedRobotGUI(robot_state, command_context)
    window.show()
    return app.exec()


if __name__ == "__main__":
    from command_context import CommandContext
    from machining_settings import MachiningSettings

    run_integrated_gui(
        MachiningSettings(),
        CommandContext(),
    )
