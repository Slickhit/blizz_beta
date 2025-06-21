import json
import re
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

from modules.chat_handler import generate_contextual_response, handle_user_input
from modules.command_executor import execute_command
from modules.port_scanner import scan_target
from modules import chat_db, summarizer
from modules.guidance_api import guidance_api


class ChatSession:
    """Representation of a single chat session."""

    def __init__(self, gui: "BlizzGUI", parent: ttk.Notebook, session_id: int) -> None:
        self.gui = gui
        self.session_id = session_id
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        self.file_path = Path(__file__).resolve().parent.parent / "sessions" / f"session_{session_id}.jsonl"
        self.file_path.parent.mkdir(exist_ok=True)

        opts = gui.common_opts
        self.chat_log = ScrolledText(self.frame, width=80, height=20, state="disabled", **opts)
        self.chat_log.pack(padx=10, pady=5)

        self.input_entry = tk.Entry(self.frame, width=80, **opts)
        self.input_entry.configure(insertbackground="#00ffcc")
        self.input_entry.pack(padx=10, pady=(0, 5))

        send_button = tk.Button(
            self.frame,
            text="Send",
            command=self.handle_input,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        send_button.pack(padx=10, pady=(0, 5))

        self.suggestion_box = ScrolledText(self.frame, width=80, height=5, state="disabled", **opts)
        self.suggestion_box.pack(padx=10, pady=5)

        self.guidance_box = ScrolledText(self.frame, width=80, height=5, state="disabled", **opts)
        self.guidance_box.pack(padx=10, pady=5)
        guidance_api.set_widget(self.guidance_box)

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

    def update_boxes(self, response: str) -> None:
        suggestion = ""
        guidance = ""

        match = re.search(r"Suggested Response:\s*(.*?)(?:\n\s*[\ud83c-\udfff]*?Guidance:|$)", response, re.S)
        if match:
            suggestion = match.group(1).strip()

        match = re.search(r"Guidance:\s*(.*)", response, re.S)
        if match:
            guidance = match.group(1).strip()

        self.suggestion_box.configure(state="normal")
        self.suggestion_box.delete("1.0", tk.END)
        if suggestion:
            self.suggestion_box.insert(tk.END, suggestion + "\n")
        self.suggestion_box.configure(state="disabled")

        self.guidance_box.configure(state="normal")
        self.guidance_box.delete("1.0", tk.END)
        self.guidance_box.configure(state="disabled")
        if guidance:
            guidance_api.push(guidance)

    def handle_input(self, event=None) -> None:  # type: ignore[override]
        user_text = self.input_entry.get().strip()
        if not user_text:
            return

        self.input_entry.delete(0, tk.END)
        self._append_text(self.chat_log, f"You: {user_text}\n")
        self.chat_log.yview(tk.END)
        self.append_history("user", user_text)

        if user_text.lower() == "exit":
            self.gui.root.quit()
            return

        if user_text.startswith("!"):
            command = user_text[1:].strip()
            response = execute_command(command)
            try:
                from modules.cli_guidance import synthesize_guidance

                hint = synthesize_guidance(command, response)
                if hint:
                    guidance_api.push(hint)
            except Exception:
                pass
        else:
            ctx_resp = generate_contextual_response(user_text)
            response = ctx_resp if ctx_resp is not None else handle_user_input(user_text)

        self._append_text(self.chat_log, f"Bot: {response}\n")
        self.chat_log.yview(tk.END)
        self.update_boxes(response)
        self.append_history("bot", response)


class BlizzGUI:
    """Tkinter interface supporting multiple chat sessions."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Blizz Beta")
        root.configure(bg="#1e1e1e")

        header = tk.Frame(root, bg="#1e1e1e")
        header.pack(anchor="nw", pady=(5, 0))
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "blizz_netic_logo.png"
        try:
            self.logo_img = tk.PhotoImage(file=str(logo_path))
            self.logo_small = self.logo_img.subsample(4, 4)
            tk.Label(header, image=self.logo_small, bg="#1e1e1e").pack(side="left", padx=(10, 5))
        except Exception:
            tk.Label(header, text="Blizz", bg="#1e1e1e", fg="#00ffcc").pack(side="left", padx=(10, 5))

        new_button = tk.Button(header, text="New Chat", command=self.add_session, bg="#1e1e1e", fg="#00ffcc")
        new_button.pack(side="left")

        scan_button = tk.Button(header, text="Scan", command=self.scan_prompt, bg="#1e1e1e", fg="#00ffcc")
        scan_button.pack(side="left", padx=(5, 0))

        sniper_button = tk.Button(header, text="Sn1per", command=self.sniper_prompt, bg="#1e1e1e", fg="#00ffcc")
        sniper_button.pack(side="left", padx=(5, 0))

        recall_button = tk.Button(header, text="Recall", command=self.recall_prompt, bg="#1e1e1e", fg="#00ffcc")
        recall_button.pack(side="left", padx=(5, 0))

        run_button = tk.Button(header, text="Run", command=self.run_prompt, bg="#1e1e1e", fg="#00ffcc")
        run_button.pack(side="left", padx=(5, 0))

        self.common_opts = {
            "font": ("Courier New", 10),
            "fg": "#00ffcc",
            "bg": "#1e1e1e",
        }

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        self.sessions: list[ChatSession] = []
        self.current_session: ChatSession | None = None

        self._rehydrate_sessions()
        if not self.sessions:
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
            guidance_api.set_widget(self.current_session.guidance_box)

    def scan_prompt(self) -> None:
        target = simpledialog.askstring("Scan", "Target?")
        if not target:
            return
        cmd = f"!scan {target}"
        if self.current_session:
            self.current_session.input_entry.insert(0, cmd)
            self.current_session.handle_input()

    def sniper_prompt(self) -> None:
        ip = simpledialog.askstring("Sn1per", "IP address?")
        if not ip:
            return
        cmd = f"sniper {ip}"
        if self.current_session:
            self.current_session.input_entry.insert(0, cmd)
            self.current_session.handle_input()

    def recall_prompt(self) -> None:
        ip = simpledialog.askstring("Recall", "IP address?")
        if not ip:
            return
        cmd = f"recall {ip}"
        if self.current_session:
            self.current_session.input_entry.insert(0, cmd)
            self.current_session.handle_input()

    def run_prompt(self) -> None:
        cmd = simpledialog.askstring("Run", "Command?")
        if not cmd:
            return
        full_cmd = f"run {cmd}"
        if self.current_session:
            self.current_session.input_entry.insert(0, full_cmd)
            self.current_session.handle_input()

    def _on_tab_change(self, event=None) -> None:
        idx = self.notebook.index("current")
        if 0 <= idx < len(self.sessions):
            self.current_session = self.sessions[idx]
            self.current_session.load_history()
            guidance_api.set_widget(self.current_session.guidance_box)


def main() -> None:
    root = tk.Tk()
    BlizzGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
