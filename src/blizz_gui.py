import json
import re
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from modules.chat_handler import generate_contextual_response, handle_user_input
from modules.command_executor import execute_command
from modules import chat_db, summarizer
from modules.guidance_api import guidance_api
from modules import dashboard


class ChatSession:
    def __init__(self, gui: "BlizzGUI", parent: ttk.Notebook, session_id: int) -> None:
        self.gui = gui
        self.session_id = session_id
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        self.file_path = Path(__file__).resolve().parent.parent / "sessions" / f"session_{session_id}.jsonl"
        self.file_path.parent.mkdir(exist_ok=True)

        opts = gui.common_opts

        # ----- Chat display -----
        chat_frame = tk.Frame(self.frame, bg="#1e1e1e")
        chat_frame.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        chat_opts = {
            **opts,
            "fg": "#ffffff",
            "bg": "#000000",
        }
        self.chat_log = ScrolledText(chat_frame, state="disabled", **chat_opts, wrap=tk.WORD)
        self.chat_log.pack(fill="both", expand=True)

        # ----- Input + Send -----
        input_frame = tk.Frame(self.frame, bg="#1e1e1e")
        input_frame.pack(fill="x", padx=10, pady=(5, 5))

        self.input_entry = ScrolledText(input_frame, height=3, **opts, wrap=tk.WORD)
        self.input_entry.configure(insertbackground="#00ffcc", relief=tk.FLAT)
        self.input_entry.pack(side="left", fill="both", expand=True, padx=(0, 5))

        send_button = tk.Button(
            input_frame,
            text="→",
            command=self.handle_input,
            font=("Courier New", 12, "bold"),
            bg="#00ffcc",
            fg="#1e1e1e",
            relief=tk.FLAT,
            width=4
        )
        send_button.pack(side="right")

        # ----- Logic output -----
        logic_frame = tk.Frame(self.frame, bg="#002244")
        logic_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5))

        logic_opts = {
            "font": ("Courier New", 10, "italic"),
            "fg": "#00ffff",
            "bg": "#002244",
        }
        self.logic_box = ScrolledText(logic_frame, height=8, state="disabled", **logic_opts, wrap=tk.WORD, relief=tk.FLAT)
        self.logic_box.pack(fill="both", expand=True)

        guidance_api.set_widget(self.logic_box)

        close_btn = tk.Button(
            self.frame,
            text="× Close",
            command=self.close_session,
            bg="#1e1e1e",
            fg="#ff6666",
            relief=tk.FLAT,
            font=("Courier New", 10, "bold")
        )
        close_btn.pack(side="top", fill="x", padx=10, pady=(0, 5))

        self.load_history()

    def cleanup(self) -> None:
        if self.file_path.exists():
            self.file_path.unlink()
        msgs = chat_db.get_messages(self.session_id)
        threading.Thread(target=summarizer.summarize_messages, args=(self.session_id, msgs)).start()
        chat_db.delete_chat(self.session_id)

    def close_session(self) -> None:
        if messagebox.askyesno("Close Chat", "Delete this chat?"):
            self.gui.delete_session(self)

    def _append_text(self, widget: ScrolledText, text: str) -> None:
        widget.configure(state="normal")
        widget.insert(tk.END, text)
        widget.configure(state="disabled")
        widget.see(tk.END)

    def append_history(self, role: str, text: str) -> None:
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"role": role, "text": text}) + "\n")
        chat_db.record_message(self.session_id, role, text)

    def load_history(self) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.delete("1.0", tk.END)
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        role = entry.get("role", "")
                        text = entry.get("text", "")
                        prefix = "You" if role == "user" else "Bot"
                        self.chat_log.insert(tk.END, f"{prefix}: {text}\n")
            except json.JSONDecodeError:
                pass
        self.chat_log.configure(state="disabled")

    def parse_response(self, response: str) -> tuple[str, str]:
        suggestion = ""
        guidance = ""
        cleaned = response

        match = re.search(r"Suggested Response:\s*(.*?)(?:\n\s*Guidance:|$)", cleaned, re.S)
        if match:
            suggestion = match.group(1).strip()
            cleaned = re.sub(r"Suggested Response:\s*(.*?)(?:\n\s*Guidance:|$)", "", cleaned, flags=re.S).strip()

        match = re.search(r"Guidance:\s*(.*)", cleaned, re.S)
        if match:
            guidance = match.group(1).strip()
            cleaned = re.sub(r"Guidance:\s*(.*)", "", cleaned, flags=re.S).strip()

        logic_parts = []
        if suggestion:
            logic_parts.append(f"Suggested: {suggestion}")
        if guidance:
            logic_parts.append(f"Guidance: {guidance}")
            guidance_api.push(f"Guidance: {guidance}")

        return cleaned, "\n".join(logic_parts)

    def structure_response(self, response: str | dict) -> tuple[str, str]:
        if isinstance(response, dict):
            chat_txt = response.get("final_response", "")
            logic_parts = []
            for key in ("thought_process", "classifications", "logic_notes"):
                val = response.get(key)
                if val:
                    label = key.replace("_", " ").title()
                    logic_parts.append(f"{label}: {val}")
            return chat_txt, "\n".join(logic_parts)
        return self.parse_response(str(response))

    def update_displays(self, chat_text: str, logic_text: str) -> None:
        self._append_text(self.chat_log, chat_text + "\n\n")
        if logic_text:
            self._append_text(self.logic_box, logic_text + "\n\n")

    def handle_input(self, event=None) -> None:
        user_text = self.input_entry.get("1.0", tk.END).strip()
        if not user_text:
            return

        self.input_entry.delete("1.0", tk.END)
        self._append_text(self.chat_log, f"You: {user_text}\n")
        self.chat_log.yview(tk.END)
        self.append_history("user", user_text)

        if user_text.lower() == "exit":
            self.gui.root.quit()
            return

        if user_text.startswith("!"):
            command = user_text[1:].strip()
            response = {
                "final_response": execute_command(command),
                "thought_process": "",
                "classifications": "",
                "logic_notes": "",
            }
            try:
                from guidance import manager as guidance_manager
                hint = guidance_manager.generate(command, response["final_response"])
                if hint:
                    guidance_api.push(hint)
            except Exception:
                pass
        else:
            ctx_resp = generate_contextual_response(user_text)
            response = {
                "final_response": ctx_resp or "",
                "thought_process": "",
                "classifications": "",
                "logic_notes": "",
            } if ctx_resp is not None else handle_user_input(user_text)

        chat_txt, logic_txt = self.structure_response(response)
        self.update_displays(f"Bot: {chat_txt}", logic_txt)
        self.append_history("bot", chat_txt)


class BlizzGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Blizz Beta")
        root.configure(bg="#1e1e1e")

        self.common_opts = {
            "font": ("Courier New", 12),
            "fg": "#00ffcc",
            "bg": "#1e1e1e",
        }

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        self.sessions: list[ChatSession] = []
        self.current_session: ChatSession | None = None

        self.add_session()

        root.bind("<Return>", lambda e: self.current_session.handle_input() if self.current_session else None)

    def add_session(self) -> None:
        session_id = len(self.sessions) + 1
        session = ChatSession(self, self.notebook, session_id)
        self.sessions.append(session)
        self.notebook.add(session.frame, text=f"Chat {session_id}")
        self.notebook.select(session.frame)
        self.current_session = session

    def delete_session(self, session: ChatSession) -> None:
        idx = self.sessions.index(session)
        self.notebook.forget(session.frame)
        session.cleanup()
        self.sessions.remove(session)
        if self.sessions:
            self.current_session = self.sessions[max(0, idx - 1)]
            self.notebook.select(self.current_session.frame)
        else:
            self.add_session()

def main():
    root = tk.Tk()
    app = BlizzGUI(root)
    root.mainloop()
