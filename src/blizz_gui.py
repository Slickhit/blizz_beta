import json
import re
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from modules.chat_handler import generate_contextual_response, handle_user_input
from modules.command_executor import execute_command


class ChatSession:
    """Representation of a single chat session."""

    def __init__(self, gui: "BlizzGUI", parent: ttk.Notebook, session_id: int) -> None:
        self.gui = gui
        self.session_id = session_id
        self.frame = tk.Frame(parent, bg="#1e1e1e")

        self.file_path = Path(__file__).resolve().parent.parent / "sessions" / f"session_{session_id}.json"
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

        # Guidance window per session
        self.guidance_window = tk.Toplevel(gui.root)
        self.guidance_window.title(f"Guidance {session_id}")
        self.guidance_window.configure(bg="#1e1e1e")
        self.guidance_box = ScrolledText(self.guidance_window, width=80, height=5, state="disabled", **opts)
        self.guidance_box.pack(padx=10, pady=5)

        self.load_history()

    def _append_text(self, widget: ScrolledText, text: str) -> None:
        widget.configure(state="normal")
        widget.insert(tk.END, text)
        widget.configure(state="disabled")
        widget.see(tk.END)

    def save_history(self, user: str, bot: str) -> None:
        data = []
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = []
        data.append({"user": user, "bot": bot})
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_history(self) -> None:
        self.chat_log.configure(state="normal")
        self.chat_log.delete("1.0", tk.END)
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for entry in data:
                    self.chat_log.insert(tk.END, f"You: {entry.get('user','')}\n")
                    self.chat_log.insert(tk.END, f"Bot: {entry.get('bot','')}\n")
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
        if guidance:
            self.guidance_box.insert(tk.END, guidance + "\n")
        self.guidance_box.configure(state="disabled")

    def handle_input(self, event=None) -> None:  # type: ignore[override]
        user_text = self.input_entry.get().strip()
        if not user_text:
            return

        self.input_entry.delete(0, tk.END)
        self._append_text(self.chat_log, f"You: {user_text}\n")
        self.chat_log.yview(tk.END)

        if user_text.lower() == "exit":
            self.gui.root.quit()
            return

        if user_text.startswith("!"):
            response = execute_command(user_text[1:].strip())
        else:
            ctx_resp = generate_contextual_response(user_text)
            response = ctx_resp if ctx_resp is not None else handle_user_input(user_text)

        self._append_text(self.chat_log, f"Bot: {response}\n")
        self.chat_log.yview(tk.END)
        self.update_boxes(response)
        self.save_history(user_text, response)


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

        self.add_session()
        root.bind("<Return>", lambda e: self.current_session.handle_input() if self.current_session else None)

    def add_session(self) -> None:
        session_id = len(self.sessions) + 1
        session = ChatSession(self, self.notebook, session_id)
        self.sessions.append(session)
        self.notebook.add(session.frame, text=f"Chat {session_id}")
        self.notebook.select(session.frame)
        self.current_session = session

    def _on_tab_change(self, event=None) -> None:
        idx = self.notebook.index("current")
        if 0 <= idx < len(self.sessions):
            self.current_session = self.sessions[idx]
            self.current_session.load_history()


def main() -> None:
    root = tk.Tk()
    BlizzGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
