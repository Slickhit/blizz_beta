import json
import re
import threading
import time
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
    """Representation of a single chat session."""

    _INSTRUCTION_PREFIXES = (
        "Bot: The main bot should respond",
    )

    def __init__(self, gui: "BlizzGUI", parent: ttk.Notebook, session_id: int) -> None:
        self.gui = gui
        self.session_id = session_id
        self.frame = tk.Frame(parent, bg="#1e1e1e")
        self.messages: list[dict] = []

        self.file_path = (
            Path(__file__).resolve().parent.parent
            / "sessions"
            / f"session_{session_id}.jsonl"
        )
        self.file_path.parent.mkdir(exist_ok=True)

        opts = gui.common_opts

        # ----- Top frame: conversation history -----
        top_frame = tk.Frame(self.frame, bg="#1e1e1e")
        top_frame.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        self.chat_log = ScrolledText(top_frame, state="disabled", **opts)
        self.chat_log.pack(fill="both", expand=True)

        # ----- Middle frame: user input -----
        middle_frame = tk.Frame(self.frame, bg="#1e1e1e")
        middle_frame.pack(fill="x", padx=10, pady=5)

        self.input_entry = ScrolledText(middle_frame, height=3, **opts)
        self.input_entry.configure(insertbackground="#00ffcc")
        self.input_entry.pack(side="left", fill="both", expand=True)

        send_button = tk.Button(
            middle_frame,
            text="Send",
            command=self.handle_input,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        send_button.pack(side="left", padx=(5, 0))

        # ----- Bottom frame: system output -----
        bottom_frame = tk.Frame(self.frame, bg="#002244")
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        logic_opts = {"font": ("Courier New", 11), "fg": "#dddddd", "bg": "#002244"}
        self.logic_box = ScrolledText(
            bottom_frame, height=10, state="disabled", **logic_opts
        )
        self.logic_box.pack(fill="both", expand=True)

        guidance_api.set_widget(self.logic_box)

        close_btn = tk.Button(
            self.frame,
            text="Close",
            command=self.close_session,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        close_btn.pack(padx=10, pady=(0, 5))

        self.load_history()

    def cleanup(self) -> None:
        if self.file_path.exists():
            self.file_path.unlink()
        msgs = chat_db.get_messages(self.session_id)
        threading.Thread(
            target=summarizer.summarize_messages, args=(self.session_id, msgs)
        ).start()
        chat_db.delete_chat(self.session_id)

    def close_session(self) -> None:
        if messagebox.askyesno("Close Chat", "Delete this chat?"):
            self.gui.delete_session(self)

    def _append_text(self, widget: ScrolledText, text: str) -> None:
        widget.configure(state="normal")
        widget.insert(tk.END, text)
        widget.configure(state="disabled")
        widget.see(tk.END)

    def render_to_top(self, msg: dict) -> None:
        prefix = "You" if msg["type"] == "user_input" else "Bot"
        self._append_text(self.chat_log, f"{prefix}: {msg['content']}\n")

    def render_to_bottom(self, msg: dict) -> None:
        self._append_text(self.logic_box, msg["content"] + "\n")

    def render_message(self, msg: dict) -> None:
        if msg["type"] in ("user_input", "assistant_response"):
            self.render_to_top(msg)
        elif msg["type"] == "system_output":
            self.render_to_bottom(msg)

    def append_history(self, role: str, text: str) -> None:
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"role": role, "text": text}) + "\n")
        chat_db.record_message(self.session_id, role, text)

    def load_history(self) -> None:
        self.messages.clear()
        self.chat_log.configure(state="normal")
        self.chat_log.delete("1.0", tk.END)
        self.logic_box.configure(state="normal")
        self.logic_box.delete("1.0", tk.END)
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        role = entry.get("role", "")
                        text = entry.get("text", "")
                        mtype = "user_input" if role == "user" else "assistant_response"
                        self.messages.append({"type": mtype, "content": text})
            except json.JSONDecodeError:
                pass
        for msg in self.messages:
            self.render_message(msg)
        self.chat_log.configure(state="disabled")
        self.logic_box.configure(state="disabled")

    def parse_response(self, response: str) -> tuple[str, str]:
        """Split a raw bot reply into chat text and system thinking."""
        # Primary delimiter based on explicit THINK tag. When present we take the
        # text before the marker as the user facing reply and everything after as
        # raw logic output with no further parsing.
        if "[[THINK]]" in response:
            chat, logic = response.split("[[THINK]]", 1)
            return chat.strip(), logic.strip()

        # Entire response is leaked instructions
        stripped = response.strip()
        for pref in self._INSTRUCTION_PREFIXES:
            if stripped.startswith(pref):
                return "", stripped

        # Fallback for "Bot: Bot:" style thinking. If present treat everything
        # from the second "Bot:" onward as raw logic meant for the bottom pane.
        botbot = re.search(r"(Bot:\s*Bot:.*)", response, re.DOTALL)
        if botbot:
            chat = response[: botbot.start()].strip()
            logic = botbot.group(1).strip()
            # strip any leading "Bot:" prefix from the chat segment
            chat = re.sub(r"^\s*Bot:\s*", "", chat).strip()
            return chat, logic

        suggestion = ""
        guidance = ""
        cleaned = response

        match = re.search(
            r"Suggested Response:\s*(.*?)(?:\n\s*Guidance:|$)", cleaned, re.S
        )
        if match:
            suggestion = match.group(1).strip()
            cleaned = re.sub(
                r"Suggested Response:\s*(.*?)(?:\n\s*Guidance:|$)",
                "",
                cleaned,
                flags=re.S,
            ).strip()

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

        logic_text = "\n".join(logic_parts)
        return cleaned, logic_text

    def structure_response(self, response: str | dict) -> tuple[str, str]:
        """Handle structured dicts or raw strings for display."""
        if isinstance(response, dict):
            # Prefer explicit user_facing_response keys if provided
            if "user_facing_response" in response or "bot_logic_output" in response:
                return (
                    response.get("user_facing_response", ""),
                    response.get("bot_logic_output", ""),
                )

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
        """Insert chat text and logic output into their respective panes."""
        if chat_text:
            chat_msg = {"type": "assistant_response", "content": chat_text}
            self.messages.append(chat_msg)
            self.render_message(chat_msg)

        # Logic text should not be treated as a persistent message. It is
        # appended only to the logic box for debugging purposes.
        if logic_text:
            self._append_text(self.logic_box, logic_text + "\n")

    def handle_input(self, event=None) -> None:  # type: ignore[override]
        user_text = self.input_entry.get("1.0", tk.END).strip()
        if not user_text:
            return

        self.input_entry.delete("1.0", tk.END)
        user_msg = {
            "type": "user_input",
            "content": user_text,
            "timestamp": time.time(),
        }
        self.messages.append(user_msg)
        self.render_message(user_msg)
        self.chat_log.yview(tk.END)
        self.append_history("user", user_text)

        threading.Thread(target=self._process_input, args=(user_text,)).start()

    def _process_input(self, user_text: str) -> None:
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
            if ctx_resp is not None:
                response = {
                    "final_response": ctx_resp,
                    "thought_process": "",
                    "classifications": "",
                    "logic_notes": "",
                }
            else:
                response = handle_user_input(user_text)

        chat_txt, logic_txt = self.structure_response(response)
        self.gui.root.after(0, lambda: self._handle_response(chat_txt, logic_txt))

    def _handle_response(self, chat_txt: str, logic_txt: str) -> None:
        # update_displays already prefixes bot messages, so pass the raw text
        # to avoid duplicating the label.
        self.update_displays(chat_txt, logic_txt)
        self.append_history("bot", chat_txt)
        if hasattr(self.gui, "dashboard"):
            dashboard.refresh_dashboard()


class BlizzGUI:
    """Tkinter interface supporting multiple chat sessions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Blizz Beta")
        root.configure(bg="#1e1e1e")

        header = tk.Frame(root, bg="#1e1e1e")
        header.pack(anchor="nw", pady=(5, 0))
        logo_path = (
            Path(__file__).resolve().parent.parent / "assets" / "blizz_netic_logo.png"
        )
        try:
            self.logo_img = tk.PhotoImage(file=str(logo_path))
            self.logo_small = self.logo_img.subsample(4, 4)
            tk.Label(header, image=self.logo_small, bg="#1e1e1e").pack(
                side="left", padx=(10, 5)
            )
        except Exception:
            tk.Label(header, text="Blizz", bg="#1e1e1e", fg="#00ffcc").pack(
                side="left", padx=(10, 5)
            )

        new_button = tk.Button(
            header,
            text="New Chat",
            command=self.add_session,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        new_button.pack(side="left")

        scan_button = tk.Button(
            header, text="Scan", command=self.scan_prompt, bg="#1e1e1e", fg="#00ffcc"
        )
        scan_button.pack(side="left", padx=(5, 0))

        sniper_button = tk.Button(
            header,
            text="Sn1per",
            command=self.sniper_prompt,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        sniper_button.pack(side="left", padx=(5, 0))

        recall_button = tk.Button(
            header,
            text="Recall",
            command=self.recall_prompt,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        recall_button.pack(side="left", padx=(5, 0))

        run_button = tk.Button(
            header, text="Run", command=self.run_prompt, bg="#1e1e1e", fg="#00ffcc"
        )
        run_button.pack(side="left", padx=(5, 0))

        self.common_opts = {
            "font": ("Courier New", 12),
            "fg": "#00ffcc",
            "bg": "#1e1e1e",
        }

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # Dashboard tab
        self.dashboard = dashboard.GUIDashboard(self.notebook)
        self.notebook.add(self.dashboard.frame, text="Dashboard")
        dashboard.set_active_dashboard(self.dashboard)

        self.sessions: list[ChatSession] = []
        self.current_session: ChatSession | None = None

        self._rehydrate_sessions()
        if not self.sessions:
            self.add_session()

        root.bind(
            "<Return>",
            lambda e: (
                self.current_session.handle_input() if self.current_session else None
            ),
        )

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

    def _rehydrate_sessions(self) -> None:
        sessions_dir = Path(__file__).resolve().parent.parent / "sessions"
        for path in sorted(sessions_dir.glob("session_*.jsonl")):
            sid = int(re.search(r"(\d+)", path.stem).group(1))
            session = ChatSession(self, self.notebook, sid)
            self.sessions.append(session)
            self.notebook.add(session.frame, text=f"Chat {sid}")
        if self.sessions:
            self.notebook.select(self.sessions[0].frame)
            self.current_session = self.sessions[0]
            guidance_api.set_widget(self.current_session.logic_box)

    def scan_prompt(self) -> None:
        target = simpledialog.askstring("Scan", "Target?")
        if not target:
            return
        cmd = f"!scan {target}"
        if self.current_session:
            self.current_session.input_entry.insert("1.0", cmd)
            self.current_session.handle_input()

    def sniper_prompt(self) -> None:
        ip = simpledialog.askstring("Sn1per", "IP address?")
        if not ip:
            return
        cmd = f"sniper {ip}"
        if self.current_session:
            self.current_session.input_entry.insert("1.0", cmd)
            self.current_session.handle_input()

    def recall_prompt(self) -> None:
        ip = simpledialog.askstring("Recall", "IP address?")
        if not ip:
            return
        cmd = f"recall {ip}"
        if self.current_session:
            self.current_session.input_entry.insert("1.0", cmd)
            self.current_session.handle_input()

    def run_prompt(self) -> None:
        cmd = simpledialog.askstring("Run", "Command?")
        if not cmd:
            return
        full_cmd = f"run {cmd}"
        if self.current_session:
            self.current_session.input_entry.insert("1.0", full_cmd)
            self.current_session.handle_input()

    def _on_tab_change(self, event=None) -> None:
        idx = self.notebook.index("current")
        if idx == self.notebook.index(self.dashboard.frame):
            self.current_session = None
            dashboard.set_active_dashboard(self.dashboard)
        else:
            session_idx = idx
            if self.dashboard.frame in self.notebook.tabs():
                session_idx -= 1
            if 0 <= session_idx < len(self.sessions):
                self.current_session = self.sessions[session_idx]
                self.current_session.load_history()
                guidance_api.set_widget(self.current_session.logic_box)


def main() -> None:
    root = tk.Tk()
    BlizzGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
