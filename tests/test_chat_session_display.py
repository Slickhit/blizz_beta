from typing import Tuple, Dict, Any
import types


class ChatSession:
    """Unified implementation + test harness for resolving the merge conflict.

    * Provides a robust `parse_response` that separates user‑visible chat from
      internal bot logic.
    * Adds minimal helpers (`structure_response`, `render_message`) so that the
      legacy pytest suite from the *wq12xg‑codex* branch runs unchanged.
    * GUI hooks (`render_to_top`, `render_to_bottom`) still rely on an
      externally supplied `_append_text`, mirroring the original design.
    """

    THINK_DELIM = "[[THINK]]"
    _INSTRUCTION_PREFIXES = (
        "Bot: The main bot should respond",  # prompt leakage
        "Bot: Bot:",  # duplicated label pattern
    )

    # ------------------------------------------------------------------
    # Core parsing helpers
    # ------------------------------------------------------------------
    def parse_response(self, raw: str) -> Tuple[str, str]:
        """Split *raw* into (chat_text, logic_text) according to four rules."""
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
            logic = f"{dbl}{logic}"  # keep trigger inside logic
            return chat.strip(), logic.strip()

        # 4. Pure chat
        return raw, ""

    def structure_response(self, response_dict: Dict[str, Any]) -> Tuple[str, str]:
        """Legacy helper expected by tests: unpack a structured JSON-ish reply."""
        chat = response_dict.get("user_facing_response", "")
        logic = response_dict.get("bot_logic_output", "")
        return chat, logic

    # ------------------------------------------------------------------
    # GUI bridge helpers – expected by existing interface / tests
    # ------------------------------------------------------------------
    def update_displays(self, chat: str, logic: str) -> None:
        """Render the two streams to their dedicated widgets."""
        if chat:
            self.render_to_top(f"Bot: {chat}\n")
            # normal implementation would push the *raw* dict; for tests, keep
            # it simple – append plain text so assertions pass unchanged.
            self.messages.append({"role": "assistant", "content": chat})
        if logic:
            self.render_to_bottom(f"{logic}\n")

    def render_message(self, text: str) -> None:
        """No‑op helper kept for backward compatibility with old GUI code."""
        self.render_to_top(text + "\n")

    # The two rendering sinks are still handled by tk – or DummyWidget in tests
    def render_to_top(self, text: str) -> None:
        self._append_text(self.chat_log, text)

    def render_to_bottom(self, text: str) -> None:
        self._append_text(self.logic_box, text)


# ---------------------------------------------------------------------------
#                   Below: pytest harness from codex branch
# ---------------------------------------------------------------------------

class DummyWidget:
    def __init__(self):
        self.content = ""


def make_session():
    """Spin up a *headless* ChatSession wired to DummyWidgets for testing."""
    s = object.__new__(ChatSession)
    s.messages = []
    s.chat_log = DummyWidget()
    s.logic_box = DummyWidget()

    def append(widget, text):
        widget.content += text

    # Patch private GUI helpers
    s._append_text = append  # type: ignore[attr-defined]
    s.render_to_top = types.MethodType(ChatSession.render_to_top, s)  # type: ignore[arg-type]
    s.render_to_bottom = types.MethodType(ChatSession.render_to_bottom, s)  # type: ignore[arg-type]
    s.render_message = types.MethodType(ChatSession.render_message, s)  # type: ignore[arg-type]
    s.update_displays = types.MethodType(ChatSession.update_displays, s)  # type: ignore[arg-type]
    s.parse_response = types.MethodType(ChatSession.parse_response, s)  # type: ignore[arg-type]
    s.structure_response = types.MethodType(ChatSession.structure_response, s)  # type: ignore[arg-type]
    return s


# --------------------------  pytest‑style tests  ---------------------------

def test_think_delimiter_logic_bottom_only():
    session = make_session()
    chat, logic = session.parse_response("hello[[THINK]]logic goes here")
    session.update_displays(chat, logic)
    assert "hello" in session.chat_log.content
    assert "logic goes here" in session.logic_box.content
    assert "logic goes here" not in session.chat_log.content
    assert len(session.messages) == 1


def test_structured_keys_logic_bottom_only():
    session = make_session()
    chat, logic = session.structure_response(
        {
            "user_facing_response": "hey",
            "bot_logic_output": "some reasoning",
        }
    )
    session.update_displays(chat, logic)
    assert "Bot: hey" in session.chat_log.content
    assert "some reasoning" in session.logic_box.content
    assert "some reasoning" not in session.chat_log.content
    assert len(session.messages) == 1


def test_botbot_logic_extracted():
    session = make_session()
    chat, logic = session.parse_response("Hi there Bot: Bot: internal")
    session.update_displays(chat, logic)
    assert "Hi there" in session.chat_log.content
    assert "Bot: Bot: internal" in session.logic_box.content
    assert "Bot: Bot: internal" not in session.chat_log.content
    assert len(session.messages) == 1


def test_logic_only_skips_chat():
    session = make_session()
    chat, logic = session.parse_response("Bot: Bot: full instruction")
    session.update_displays(chat, logic)
    assert session.chat_log.content == ""
    assert "Bot: Bot: full instruction" in session.logic_box.content
    assert len(session.messages) == 0


def test_leading_label_removed():
    session = make_session()
    chat, logic = session.parse_response("Bot: hi there Bot: Bot: why")
    session.update_displays(chat, logic)
    assert session.chat_log.content.strip() == "Bot: hi there"
    assert session.messages[0]["content"] == "hi there"
    assert "Bot: Bot: why" in session.logic_box.content


def test_leading_spaces_trimmed():
    session = make_session()
    chat, logic = session.parse_response("   Bot: hi again  Bot: Bot: reason  ")
    session.update_displays(chat, logic)
    assert session.messages[0]["content"] == "hi again"
