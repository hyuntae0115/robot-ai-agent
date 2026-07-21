import tkinter as tk

from controller import handle_user_input
from voice import listen_voice


def run_gui(robot_state):
    command_history = []
    history_index = -1

    root = tk.Tk()
    root.title("Robot AI Agent Test GUI")
    root.geometry("700x500")

    def show_llm_json(text):
        json_text.insert(tk.END, text + "\n\n")
        json_text.see(tk.END)

    def show_result(text):
        result_text.insert(tk.END, text + "\n\n")
        result_text.see(tk.END)

    def show_state():
        state_text.insert(
            tk.END,
            robot_state.get_status() + "\n\n"
        )
        state_text.see(tk.END)

    def run_voice_command():
        voice_text = listen_voice()

        if not voice_text:
            show_result("음성을 인식하지 못했습니다.")
            return

        command_entry.delete(0, tk.END)
        command_entry.insert(0, voice_text)
        command_entry.focus_set()

        run_text_command()

    def run_text_command(event=None):
        nonlocal history_index

        user_input = command_entry.get().strip()

        if not user_input:
            show_result("명령을 입력하세요.")
            return

        command_history.append(user_input)
        history_index = len(command_history)

        results, raw_output = handle_user_input(
            user_input,
            robot_state
        )

        show_llm_json(raw_output)
        show_result("\n".join(results))
        show_state()

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

    command_label = tk.Label(root, text="Command")
    command_label.pack()

    command_entry = tk.Entry(root, width=70)
    command_entry.pack(pady=5)

    command_entry.bind("<Return>", run_text_command)
    command_entry.bind("<Up>", show_previous_command)
    command_entry.bind("<Down>", show_next_command)

    run_button = tk.Button(
        root,
        text="텍스트 실행",
        command=run_text_command
    )
    run_button.pack(pady=5)

    voice_button = tk.Button(
        root,
        text="음성 인식",
        command=run_voice_command
    )
    voice_button.pack(pady=5)

    json_label = tk.Label(root, text="LLM JSON")
    json_label.pack()

    json_text = tk.Text(root, height=8, width=80)
    json_text.pack(pady=5)

    result_label = tk.Label(root, text="Execute Result")
    result_label.pack()

    result_text = tk.Text(root, height=8, width=80)
    result_text.pack(pady=5)

    state_label = tk.Label(root, text="Robot State")
    state_label.pack()

    state_text = tk.Text(root, height=80, width=80)
    state_text.pack(pady=5)

    show_state()
    command_entry.focus_set()

    root.mainloop()