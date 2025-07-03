from typing import Tuple

class ChatSession:
    """Patch of ChatSession focusing on reliably separating user‑facing text from bot logic."""

    THINK_DELIM = "[[THINK]]"
    _INSTRUCTION_PREFIXES = (
        "Bot: The main bot should respond",  # prompt leakage
        "Bot: Bot:",  # duplicated label pattern
    )

    # ---------------------------------------------------------------------
    # Public helpers – these are the only two that your GUI should call.
    # ---------------------------------------------------------------------
    def parse_response(self, raw: str) -> Tuple[str, str]:
        """Split *raw* into (chat_text, logic_text).

        Rules (in order):
        1. If [[THINK]] appears → everything right of it is logic.
        2. If the response starts with a leaked instruction prefix → treat the *whole* thing as logic.
        3. If we detect the doubled "Bot: Bot:" pattern anywhere → split at the first occurrence.
        4. Otherwise treat the message as pure chat.
        """
        raw = raw.strip()
        if not raw:
            return "", ""

        # 1. Explicit THINK delimiter
        if self.THINK_DELIM in raw:
            chat, logic = raw.split(self.THINK_DELIM, 1)
            return chat.strip(), logic.strip()

        # 2. Full leaked system instruction
        for pref in self._INSTRUCTION_PREFIXES:
            if raw.startswith(pref):
                return "", raw

        # 3. In‑line "Bot: Bot:" logic leakage
        dbl = "Bot: Bot:"
        if dbl in raw:
            chat, logic = raw.split(dbl, 1)
            # keep the triggering prefix inside logic for clarity
            logic = f"{dbl}{logic}"
            return chat.strip(), logic.strip()

        # 4. Pure chat
        return raw, ""

    # ------------------------------------------------------------------
    # GUI bridge helpers – expected by the existing interface.
    # ------------------------------------------------------------------
    def update_displays(self, chat: str, logic: str) -> None:
        """Render the two streams to their dedicated widgets."""
        if chat:
            # prepend label once here so tests can assert on "Bot: " prefix
            self.render_to_top(f"Bot: {chat}\n")
            self.messages.append(chat)
        if logic:
            self.render_to_bottom(f"{logic}\n")

    # The two rendering sinks are still handled by tk.
    def render_to_top(self, text: str) -> None:
        self._append_text(self.chat_log, text)

    def render_to_bottom(self, text: str) -> None:
        self._append_text(self.logic_box, text)
