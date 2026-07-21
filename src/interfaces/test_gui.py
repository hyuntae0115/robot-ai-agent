import threading
import tkinter as tk

from controller import handle_user_input
from voice import listen_voice


def run_gui(robot_state):
    command_history = []
    history_index = -1

    root = tk.Tk()
    root.title("Robot AI Agent Test GUI")
    root.geometry("700x850")

    def show_llm_json(text):
        json_text.insert(
            tk.END,
            text + "\n\n"
        )
        json_text.see(tk.END)

    def show_result(text):
        result_text.insert(
            tk.END,
            text + "\n\n"
        )
        result_text.see(tk.END)

    def show_state():
        state_text.insert(
            tk.END,
            robot_state.get_status() + "\n\n"
        )
        state_text.see(tk.END)

    def show_voice_result(
        raw_text: str,
        normalized_text: str
    ):
        voice_result_text.config(state="normal")
        voice_result_text.delete("1.0", tk.END)

        voice_result_text.insert(
            tk.END,
            "Whisper 원본\n"
            f"{raw_text}\n\n"
            "보정된 음성 명령\n"
            f"{normalized_text}"
        )

        voice_result_text.see("1.0")
        voice_result_text.config(state="disabled")

    def update_voice_status(message: str):
        root.after(
            0,
            lambda: voice_status_label.config(
                text=message
            )
        )

    def finish_voice_command(
        raw_text: str,
        normalized_text: str
    ):
        voice_button.config(state="normal")
        run_button.config(state="normal")

        if not normalized_text:
            voice_status_label.config(
                text="음성을 인식하지 못했습니다."
            )

            show_result(
                "음성을 인식하지 못했습니다."
            )

            command_entry.focus_set()
            return

        show_voice_result(
            raw_text,
            normalized_text
        )

        command_entry.delete(0, tk.END)
        command_entry.insert(
            0,
            normalized_text
        )

        voice_status_label.config(
            text="음성 인식이 완료되었습니다."
        )

        command_entry.focus_set()

        run_text_command()

    def handle_voice_error(error: Exception):
        voice_button.config(state="normal")
        run_button.config(state="normal")

        voice_status_label.config(
            text="음성 처리 중 오류가 발생했습니다."
        )

        show_result(
            "음성 처리 오류\n"
            f"{error}"
        )

        command_entry.focus_set()

    def run_voice_command():
        voice_button.config(state="disabled")
        run_button.config(state="disabled")

        voice_status_label.config(
            text="음성 입력을 준비하고 있습니다."
        )

        def voice_task():
            try:
                raw_text, normalized_text = listen_voice(
                    status_callback=update_voice_status
                )

                root.after(
                    0,
                    lambda: finish_voice_command(
                        raw_text,
                        normalized_text
                    )
                )

            except Exception as error:
                root.after(
                    0,
                    lambda: handle_voice_error(error)
                )

        voice_thread = threading.Thread(
            target=voice_task,
            daemon=True
        )

        voice_thread.start()

    def run_text_command(event=None):
        nonlocal history_index

        user_input = command_entry.get().strip()

        if not user_input:
            show_result("명령을 입력하세요.")
            return

        command_history.append(user_input)
        history_index = len(command_history)

        try:
            results, raw_output = handle_user_input(
                user_input,
                robot_state
            )

            show_llm_json(raw_output)
            show_result("\n".join(results))
            show_state()

        except Exception as error:
            show_result(
                "명령 처리 중 오류가 발생했습니다.\n"
                f"{error}"
            )

        finally:
            command_entry.delete(0, tk.END)
            command_entry.focus_set()

    def show_previous_command(event=None):
        nonlocal history_index

        if not command_history:
            return

        if history_index > 0:
            history_index -= 1

        command_entry.delete(0, tk.END)
        command_entry.insert(
            0,
            command_history[history_index]
        )

    def show_next_command(event=None):
        nonlocal history_index

        if not command_history:
            return

        if history_index < len(command_history) - 1:
            history_index += 1

            command_entry.delete(0, tk.END)
            command_entry.insert(
                0,
                command_history[history_index]
            )

        else:
            history_index = len(command_history)
            command_entry.delete(0, tk.END)

    # ---------------- GUI ---------------- #

    title_label = tk.Label(
        root,
        text="Robot AI Agent Test GUI",
        font=("Arial", 16)
    )
    title_label.pack(pady=10)

    command_label = tk.Label(
        root,
        text="Command"
    )
    command_label.pack()

    command_entry = tk.Entry(
        root,
        width=70
    )
    command_entry.pack(pady=5)

    command_entry.bind(
        "<Return>",
        run_text_command
    )

    command_entry.bind(
        "<Up>",
        show_previous_command
    )

    command_entry.bind(
        "<Down>",
        show_next_command
    )

    run_button = tk.Button(
        root,
        text="텍스트 실행",
        command=run_text_command
    )
    run_button.pack(pady=5)

    voice_status_label = tk.Label(
        root,
        text="음성 인식을 하려면 음성 인식 버튼을 눌러주세요.",
        font=("Arial", 10),
        justify="center"
    )
    voice_status_label.pack(pady=5)

    voice_button = tk.Button(
        root,
        text="음성 인식",
        command=run_voice_command
    )
    voice_button.pack(pady=5)

    voice_result_label = tk.Label(
        root,
        text="Voice Recognition Result"
    )
    voice_result_label.pack()

    voice_result_text = tk.Text(
        root,
        height=5,
        width=80,
        wrap=tk.WORD
    )
    voice_result_text.pack(pady=5)
    voice_result_text.config(state="disabled")

    json_label = tk.Label(
        root,
        text="LLM JSON"
    )
    json_label.pack()

    json_text = tk.Text(
        root,
        height=6,
        width=80,
        wrap=tk.WORD
    )
    json_text.pack(pady=5)

    result_label = tk.Label(
        root,
        text="Execute Result"
    )
    result_label.pack()

    result_text = tk.Text(
        root,
        height=6,
        width=80,
        wrap=tk.WORD
    )
    result_text.pack(pady=5)

    state_label = tk.Label(
        root,
        text="Robot State"
    )
    state_label.pack()

    state_text = tk.Text(
        root,
        height=8,
        width=80,
        wrap=tk.WORD
    )
    state_text.pack(pady=5)

    show_state()
    command_entry.focus_set()

    root.mainloop()