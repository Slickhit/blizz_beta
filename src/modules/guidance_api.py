from tkinter.scrolledtext import ScrolledText


class GuidancePane:
    def __init__(self) -> None:
        self.widget: ScrolledText | None = None

    def set_widget(self, widget: ScrolledText | None) -> None:
        self.widget = widget

    def push(self, text: str) -> None:
        if self.widget is None:
            return
        self.widget.configure(state="normal")
        self.widget.insert("end", text + "\n")
        self.widget.configure(state="disabled")
        self.widget.see("end")

guidance_api = GuidancePane()
