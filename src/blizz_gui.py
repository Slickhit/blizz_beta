import re
from pathlib import Path
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from modules.chat_handler import generate_contextual_response, handle_user_input
from modules.command_executor import execute_command


class BlizzGUI:
    """Simple Tkinter interface for the chat assistant."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Blizz Beta")
        root.configure(bg="#1e1e1e")

        logo_frame = tk.Frame(root, bg="#1e1e1e")
        logo_frame.pack(pady=(10, 5))
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "blizz_netic_logo.png"
        self.logo_img = tk.PhotoImage(file=str(logo_path))
        logo_label = tk.Label(logo_frame, image=self.logo_img, bg="#1e1e1e")
        logo_label.pack()

        common_opts = {
            "font": ("Courier New", 10),
            "fg": "#00ffcc",
            "bg": "#1e1e1e",
        }

        self.chat_log = ScrolledText(root, width=80, height=20, state="disabled", **common_opts)
        self.chat_log.pack(padx=10, pady=5)

        self.input_entry = tk.Entry(root, width=80, **common_opts)
        self.input_entry.configure(insertbackground="#00ffcc")
        self.input_entry.pack(padx=10, pady=(0, 5))

        # Allow pressing Enter anywhere in the window to send the message
        root.bind("<Return>", self.handle_input)

        send_button = tk.Button(
            root,
            text="Send",
            command=self.handle_input,
            bg="#1e1e1e",
            fg="#00ffcc",
        )
        send_button.pack(padx=10, pady=(0, 5))

        self.suggestion_box = ScrolledText(root, width=80, height=5, state="disabled", **common_opts)
        self.suggestion_box.pack(padx=10, pady=5)

        self.guidance_box = ScrolledText(root, width=80, height=5, state="disabled", **common_opts)
        self.guidance_box.pack(padx=10, pady=5)

    def _append_text(self, widget: ScrolledText, text: str) -> None:
        widget.configure(state="normal")
        widget.insert(tk.END, text)
        widget.configure(state="disabled")
        widget.see(tk.END)

    def update_boxes(self, response: str) -> None:
        """Update the Suggested Response and Guidance boxes."""
        suggestion = ""
        guidance = ""

        match = re.search(r"Suggested Response:\s*(.*?)(?:\n\s*[\ud83c-\udfff]* ?Guidance:|$)", response, re.S)
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
            self.root.quit()
            return

        if user_text.startswith("!"):
            response = execute_command(user_text[1:].strip())
        else:
            ctx_resp = generate_contextual_response(user_text)
            response = ctx_resp if ctx_resp is not None else handle_user_input(user_text)

        self._append_text(self.chat_log, f"Bot: {response}\n")
        self.chat_log.yview(tk.END)
        self.update_boxes(response)


def main() -> None:
    root = tk.Tk()
    BlizzGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
