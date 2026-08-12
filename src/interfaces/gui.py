import json
import threading
import tkinter as tk

import customtkinter as ctk

from controller import execute_pending_command, handle_user_input
from isaac_client import send_drilling_command
from voice import listen_voice


COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "surface_light": "#EAF0F8",
    "border": "#D5DFEC",
    "primary": "#AFCBF3",
    "primary_hover": "#94B8EA",
    "success": "#16895A",
    "success_hover": "#117A50",
    "danger": "#E4B3B5",
    "danger_hover": "#D6979A",
    "warning": "#D8C28E",
    "text": "#000000",
    "text_muted": "#333333",
    "assistant_bubble": "#F0F3F7",
    "user_bubble": "#B7CFF0",
}

FONT_FAMILY = "Segoe UI"


def run_gui(robot_state, command_context):
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    command_history = []
    history_index = -1
    chat_row = 0

    root = ctk.CTk(fg_color=COLORS["background"])
    root.title("Robot AI Agent")
    root.geometry("1180x820")
    root.minsize(1020, 720)

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    def format_position_m(value):
        if value is None:
            return "—"
        return f"{value / 1000.0:.3f} m"

    def format_value(value, unit=""):
        if value is None:
            return "—"
        return f"{value} {unit}".strip()

    def set_text(widget, text, append=False):
        widget.configure(state="normal")
        if not append:
            widget.delete("1.0", "end")
        widget.insert("end", str(text))
        if append:
            widget.insert("end", "\n\n")
        widget.see("end")
        widget.configure(state="disabled")

    def show_result(text):
        add_chat_message("assistant", text)
        output_tabs.set("처리 결과")

    def add_chat_message(role, text):
        nonlocal chat_row

        is_user = role == "user"
        row_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        row_frame.grid(row=chat_row, column=0, padx=8, pady=5, sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)

        bubble = ctk.CTkFrame(
            row_frame,
            fg_color=(
                COLORS["user_bubble"]
                if is_user
                else COLORS["assistant_bubble"]
            ),
            corner_radius=14,
        )
        bubble.grid(
            row=0,
            column=0,
            padx=(90, 4) if is_user else (4, 90),
            sticky="e" if is_user else "w",
        )

        sender = "사용자" if is_user else "Robot AI Agent"
        ctk.CTkLabel(
            bubble,
            text=sender,
            font=(FONT_FAMILY, 10, "bold"),
            text_color="#000000",
            anchor="w",
        ).pack(fill="x", padx=14, pady=(9, 1))

        ctk.CTkLabel(
            bubble,
            text=str(text),
            font=(FONT_FAMILY, 12),
            text_color="#000000",
            justify="left",
            anchor="w",
            wraplength=430,
        ).pack(fill="x", padx=14, pady=(1, 10))

        chat_row += 1
        root.after(10, scroll_chat_to_bottom)

    def scroll_chat_to_bottom():
        try:
            chat_frame._parent_canvas.yview_moveto(1.0)
        except (AttributeError, tk.TclError):
            pass

    def show_llm_json(text):
        set_text(json_text, text, append=True)

    def set_connection_status(text, color):
        connection_dot.configure(text_color=color)
        connection_label.configure(text=text, text_color=color)

    def set_app_status(text):
        app_status_label.configure(text=text)

    def update_card(labels, target, machine):
        values = {
            "x": format_position_m(target.get("x")),
            "y": format_position_m(target.get("y")),
            "z": format_position_m(target.get("z")),
            "material": format_value(machine.get("material")),
            "process": format_value(machine.get("process")),
            "tool": format_value(machine.get("tool")),
            "diameter": format_value(machine.get("diameter"), "mm"),
            "depth": format_value(machine.get("depth"), "mm"),
            "rpm": format_value(machine.get("rpm"), "RPM"),
            "feed": format_value(machine.get("feed"), "mm/rev"),
        }

        for key, value in values.items():
            labels[key].configure(text=value)

    def update_pending_card():
        update_card(
            pending_value_labels,
            command_context.pending_target,
            command_context.pending_machine,
        )

        missing_fields = command_context.get_missing_fields()
        if missing_fields:
            execute_button.configure(
                state="disabled",
                fg_color="#B1DCC7",
                hover_color="#B1DCC7",
            )
            pending_badge.configure(
                text=f"입력 필요 {len(missing_fields)}",
                text_color="#000000",
            )
        else:
            execute_button.configure(
                state="normal",
                fg_color=COLORS["success"],
                hover_color=COLORS["success_hover"],
            )
            pending_badge.configure(
                text="실행 준비 완료",
                text_color="#000000",
            )

    def update_applied_card():
        target = robot_state.target_position
        machine = {
            "material": robot_state.material,
            "process": robot_state.process,
            "tool": robot_state.tool,
            "diameter": robot_state.diameter,
            "depth": robot_state.depth,
            "rpm": robot_state.rpm,
            "feed": robot_state.feed,
        }
        update_card(applied_value_labels, target, machine)

    def update_all_cards():
        update_pending_card()
        update_applied_card()

    def show_voice_result(raw_text, normalized_text):
        set_text(
            voice_result_text,
            "Whisper 원본\n"
            f"{raw_text}\n\n"
            "보정된 음성 명령\n"
            f"{normalized_text}",
        )

    def update_voice_status(message):
        root.after(
            0,
            lambda: (
                voice_status_label.configure(text=message),
                set_app_status(message),
            ),
        )

    def finish_voice_command(raw_text, normalized_text):
        voice_button.configure(state="normal")
        analyze_button.configure(state="normal")

        if not normalized_text:
            message = "음성을 인식하지 못했습니다."
            voice_status_label.configure(text=message)
            set_app_status(message)
            show_result(message)
            command_entry.focus_set()
            return

        show_voice_result(raw_text, normalized_text)
        output_tabs.set("음성 인식")

        command_entry.delete(0, "end")
        command_entry.insert(0, normalized_text)
        voice_status_label.configure(text="음성 인식이 완료되었습니다.")
        run_text_command()

    def handle_voice_error(error):
        voice_button.configure(state="normal")
        analyze_button.configure(state="normal")
        message = f"음성 처리 오류: {error}"
        voice_status_label.configure(text=message)
        set_app_status("음성 처리 실패")
        show_result(message)
        command_entry.focus_set()

    def run_voice_command():
        voice_button.configure(state="disabled")
        analyze_button.configure(state="disabled")
        voice_status_label.configure(text="음성 입력을 준비하고 있습니다.")
        set_app_status("음성 입력 준비 중")

        def voice_task():
            try:
                raw_text, normalized_text = listen_voice(
                    status_callback=update_voice_status
                )
                root.after(
                    0,
                    lambda: finish_voice_command(raw_text, normalized_text),
                )
            except Exception as error:
                root.after(
                    0,
                    lambda error=error: handle_voice_error(error),
                )

        threading.Thread(target=voice_task, daemon=True).start()

    def run_text_command(event=None):
        nonlocal history_index

        user_input = command_entry.get().strip()
        if not user_input:
            show_result("명령을 입력하세요.")
            return

        command_history.append(user_input)
        history_index = len(command_history)
        add_chat_message("user", user_input)
        output_tabs.set("처리 결과")
        set_app_status("명령 분석 중")
        analyze_button.configure(state="disabled")

        try:
            results, raw_output = handle_user_input(
                user_input,
                robot_state,
                command_context,
            )

            show_llm_json(raw_output)
            if results:
                show_result("\n".join(results))

            update_all_cards()
            set_app_status("명령 분석 완료")

        except Exception as error:
            show_result(f"명령 처리 중 오류가 발생했습니다.\n{error}")
            set_app_status("명령 처리 실패")

        finally:
            analyze_button.configure(state="normal")
            command_entry.delete(0, "end")
            command_entry.focus_set()

    def finish_drilling_send(response):
        set_connection_status("Isaac Sim 연결됨", COLORS["success"])
        set_app_status("드릴링 명령 전송 완료")
        show_result(
            "Isaac Sim 드릴링 명령 전송 성공\n"
            f"{response.get('message', response)}"
        )
        command_entry.focus_set()

    def handle_drilling_send_error(error):
        set_connection_status("Isaac Sim 연결 실패", COLORS["danger"])
        set_app_status("드릴링 명령 전송 실패")
        show_result(f"Isaac Sim 드릴링 명령 전송 실패\n{error}")
        command_entry.focus_set()

    def send_drilling_async(drilling_request):
        set_connection_status("Isaac Sim 전송 중", COLORS["warning"])
        set_app_status("드릴링 명령 전송 중")
        show_result(
            "Isaac Sim으로 드릴링 명령을 전송합니다.\n"
            f"{json.dumps(drilling_request, ensure_ascii=False)}"
        )

        def send_task():
            try:
                response = send_drilling_command(drilling_request)
                root.after(
                    0,
                    lambda response=response: finish_drilling_send(response),
                )
            except Exception as error:
                root.after(
                    0,
                    lambda error=error: handle_drilling_send_error(error),
                )

        threading.Thread(target=send_task, daemon=True).start()

    def run_pending_command():
        missing_fields = command_context.get_missing_fields()
        if missing_fields:
            names = ", ".join(field for _, field in missing_fields)
            show_result(f"드릴링 필수 정보가 부족합니다.\n{names}")
            update_pending_card()
            return

        target = dict(command_context.pending_target)
        machine = dict(command_context.pending_machine)

        try:
            results = execute_pending_command(robot_state, command_context)
            if results:
                show_result("\n".join(results))

            update_all_cards()

            drilling_request = {
                "command": "run_drilling",
                "material": machine["material"],
                "x": target["x"] / 1000.0,
                "y": target["y"] / 1000.0,
                "z": target["z"] / 1000.0,
                "depth_mm": machine["depth"],
            }

            if machine["rpm"] is not None:
                drilling_request["rpm"] = machine["rpm"]
            if machine["feed"] is not None:
                drilling_request["feed_mm_rev"] = machine["feed"]

            send_drilling_async(drilling_request)

        except Exception as error:
            show_result(f"작업 실행 중 오류가 발생했습니다.\n{error}")
            set_app_status("작업 실행 실패")

    def clear_pending_command():
        command_context.clear_pending()
        update_pending_card()
        show_result("작성 중인 작업을 취소했습니다.")
        set_app_status("작성 중 작업 취소")
        command_entry.focus_set()

    def show_previous_command(event=None):
        nonlocal history_index
        if not command_history:
            return
        if history_index > 0:
            history_index -= 1
        command_entry.delete(0, "end")
        command_entry.insert(0, command_history[history_index])

    def show_next_command(event=None):
        nonlocal history_index
        if not command_history:
            return
        if history_index < len(command_history) - 1:
            history_index += 1
            command_entry.delete(0, "end")
            command_entry.insert(0, command_history[history_index])
        else:
            history_index = len(command_history)
            command_entry.delete(0, "end")

    def create_status_card(parent, title, badge_text):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["surface"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            card,
            text=title,
            font=(FONT_FAMILY, 17, "bold"),
            text_color="#000000",
        ).grid(row=0, column=0, padx=18, pady=(16, 12), sticky="w")

        badge = ctk.CTkLabel(
            card,
            text=badge_text,
            font=(FONT_FAMILY, 11, "bold"),
            text_color="#000000",
        )
        badge.grid(row=0, column=1, padx=18, pady=(16, 12), sticky="e")

        labels = {}
        fields = (
            ("x", "X 위치"),
            ("y", "Y 위치"),
            ("z", "Z 위치"),
            ("material", "재료"),
            ("process", "공정"),
            ("tool", "공구"),
            ("diameter", "직경"),
            ("depth", "깊이"),
            ("rpm", "회전속도"),
            ("feed", "이송량"),
        )

        for row, (key, label_text) in enumerate(fields, start=1):
            ctk.CTkLabel(
                card,
                text=label_text,
                font=(FONT_FAMILY, 12),
                text_color="#000000",
            ).grid(row=row, column=0, padx=18, pady=3, sticky="w")

            value_label = ctk.CTkLabel(
                card,
                text="—",
                font=("Consolas", 13, "bold"),
                text_color="#000000",
            )
            value_label.grid(row=row, column=1, padx=18, pady=3, sticky="e")
            labels[key] = value_label

        ctk.CTkLabel(card, text="").grid(row=len(fields) + 1, column=0, pady=5)
        return card, labels, badge

    # Header
    header = ctk.CTkFrame(root, fg_color="transparent")
    header.grid(row=0, column=0, padx=28, pady=(20, 12), sticky="ew")
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        header,
        text="Robot AI Agent",
        font=(FONT_FAMILY, 25, "bold"),
        text_color="#000000",
    ).grid(row=0, column=0, sticky="w")

    ctk.CTkLabel(
        header,
        text="자연어 기반 로봇 드릴링 제어",
        font=(FONT_FAMILY, 12),
        text_color="#000000",
    ).grid(row=1, column=0, pady=(2, 0), sticky="w")

    connection_frame = ctk.CTkFrame(
        header,
        fg_color=COLORS["surface"],
        corner_radius=18,
    )
    connection_frame.grid(row=0, column=1, rowspan=2, sticky="e")

    connection_dot = ctk.CTkLabel(
        connection_frame,
        text="●",
        width=20,
        text_color="#000000",
    )
    connection_dot.pack(side="left", padx=(12, 2), pady=7)

    connection_label = ctk.CTkLabel(
        connection_frame,
        text="Isaac Sim 대기",
        font=(FONT_FAMILY, 11, "bold"),
        text_color="#000000",
    )
    connection_label.pack(side="left", padx=(2, 12), pady=7)

    # Main content
    content = ctk.CTkFrame(root, fg_color="transparent")
    content.grid(row=1, column=0, padx=28, pady=(0, 14), sticky="nsew")
    content.grid_columnconfigure(0, weight=5)
    content.grid_columnconfigure(1, weight=7)
    content.grid_rowconfigure(0, weight=1)

    # ---------------------------------------------------------
    # Left panel: chat + command input
    # ---------------------------------------------------------
    left_panel = ctk.CTkFrame(content, fg_color="transparent")
    left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
    left_panel.grid_columnconfigure(0, weight=1)
    left_panel.grid_rowconfigure(0, weight=1)

    output_panel = ctk.CTkFrame(left_panel, fg_color="transparent")
    output_panel.grid(row=0, column=0, sticky="nsew")
    output_panel.grid_columnconfigure(0, weight=1)
    output_panel.grid_rowconfigure(1, weight=1)

    voice_status_label = ctk.CTkLabel(
        output_panel,
        text="음성 인식을 하려면 음성 인식 버튼을 눌러주세요.",
        anchor="w",
        font=(FONT_FAMILY, 11),
        text_color="#000000",
    )
    voice_status_label.grid(row=0, column=0, pady=(0, 6), sticky="ew")

    output_tabs = ctk.CTkTabview(
        output_panel,
        fg_color=COLORS["surface"],
        segmented_button_fg_color=COLORS["surface_light"],
        segmented_button_selected_color=COLORS["primary"],
        segmented_button_selected_hover_color=COLORS["primary_hover"],
        text_color="#000000",
        segmented_button_unselected_color=COLORS["surface_light"],
        segmented_button_unselected_hover_color=COLORS["border"],
        corner_radius=14,
    )
    output_tabs.grid(row=1, column=0, sticky="nsew")
    output_tabs.add("처리 결과")
    output_tabs.add("LLM JSON")
    output_tabs.add("음성 인식")

    chat_frame = ctk.CTkScrollableFrame(
        output_tabs.tab("처리 결과"),
        fg_color=COLORS["background"],
        corner_radius=10,
        border_width=1,
        border_color=COLORS["border"],
    )
    chat_frame.pack(fill="both", expand=True, padx=8, pady=8)
    chat_frame.grid_columnconfigure(0, weight=1)

    def create_output_text(tab_name):
        textbox = ctk.CTkTextbox(
            output_tabs.tab(tab_name),
            wrap="word",
            font=("Consolas", 12),
            fg_color=COLORS["background"],
            text_color="#000000",
            border_width=1,
            border_color=COLORS["border"],
        )
        textbox.pack(fill="both", expand=True, padx=8, pady=8)
        textbox.configure(state="disabled")
        return textbox

    json_text = create_output_text("LLM JSON")
    voice_result_text = create_output_text("음성 인식")

    # Command input directly below the chat panel
    command_frame = ctk.CTkFrame(
        left_panel,
        fg_color=COLORS["surface"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    command_frame.grid(row=1, column=0, pady=(10, 0), sticky="ew")
    command_frame.grid_columnconfigure(0, weight=1)

    command_entry = ctk.CTkEntry(
        command_frame,
        height=44,
        placeholder_text="예: 알루미늄을 x 1123, y 0, z 1000에서 깊이 4mm로 드릴링해줘",
        font=(FONT_FAMILY, 13),
        fg_color=COLORS["surface_light"],
        border_color=COLORS["border"],
    )
    command_entry.grid(
        row=0,
        column=0,
        columnspan=2,
        padx=14,
        pady=(14, 8),
        sticky="ew",
    )
    command_entry.bind("<Return>", run_text_command)
    command_entry.bind("<Up>", show_previous_command)
    command_entry.bind("<Down>", show_next_command)

    analyze_button = ctk.CTkButton(
        command_frame,
        text="입력",
        height=40,
        command=run_text_command,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=(FONT_FAMILY, 12, "bold"),
        text_color="#000000",
    )
    analyze_button.grid(
        row=1,
        column=0,
        padx=(14, 6),
        pady=(0, 14),
        sticky="ew",
    )

    voice_button = ctk.CTkButton(
        command_frame,
        text="음성 인식",
        height=40,
        command=run_voice_command,
        fg_color=COLORS["surface_light"],
        hover_color=COLORS["border"],
        font=(FONT_FAMILY, 12, "bold"),
        text_color="#000000",
    )
    voice_button.grid(
        row=1,
        column=1,
        padx=(6, 14),
        pady=(0, 14),
        sticky="ew",
    )

    # ---------------------------------------------------------
    # Right panel: pending/applied status cards side by side
    # ---------------------------------------------------------
    right_panel = ctk.CTkFrame(content, fg_color="transparent")
    right_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
    right_panel.grid_columnconfigure(0, weight=1)
    right_panel.grid_rowconfigure(0, weight=1)

    cards_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    cards_frame.grid(row=0, column=0, sticky="nsew")
    cards_frame.grid_columnconfigure(0, weight=1)
    cards_frame.grid_columnconfigure(1, weight=1)
    cards_frame.grid_rowconfigure(0, weight=1)

    pending_card, pending_value_labels, pending_badge = create_status_card(
        cards_frame, "작성 중인 작업", "입력 대기"
    )
    pending_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

    applied_card, applied_value_labels, applied_badge = create_status_card(
        cards_frame, "적용된 작업", "Robot State"
    )
    applied_card.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

    action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
    action_frame.grid(row=1, column=0, pady=(12, 0), sticky="ew")
    action_frame.grid_columnconfigure(0, weight=1)
    action_frame.grid_columnconfigure(1, weight=1)

    clear_button = ctk.CTkButton(
        action_frame,
        text="작성 중 작업 취소",
        height=42,
        command=clear_pending_command,
        fg_color=COLORS["surface_light"],
        hover_color=COLORS["border"],
        font=(FONT_FAMILY, 12, "bold"),
        text_color="#000000",
    )
    clear_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

    execute_button = ctk.CTkButton(
        action_frame,
        text="작업 실행",
        height=42,
        command=run_pending_command,
        state="disabled",
        fg_color="#B1DCC7",
        hover_color=COLORS["success_hover"],
        font=(FONT_FAMILY, 12, "bold"),
        text_color="#000000",
    )
    execute_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    # Status bar
    status_bar = ctk.CTkFrame(
        root,
        height=34,
        fg_color=COLORS["surface"],
        corner_radius=0,
    )
    status_bar.grid(row=3, column=0, sticky="ew")
    status_bar.grid_columnconfigure(0, weight=1)

    app_status_label = ctk.CTkLabel(
        status_bar,
        text="대기 중",
        font=(FONT_FAMILY, 11),
        text_color="#000000",
    )
    app_status_label.grid(row=0, column=0, padx=28, pady=6, sticky="w")

    ctk.CTkLabel(
        status_bar,
        text="Isaac Sim  220.149.217.38:5000",
        font=("Consolas", 10),
        text_color="#000000",
    ).grid(row=0, column=1, padx=28, pady=6, sticky="e")

    update_all_cards()
    add_chat_message(
        "assistant",
        "안녕하세요. 자연어 또는 음성으로 드릴링 작업을 입력해주세요.",
    )
    command_entry.focus_set()
    root.mainloop()