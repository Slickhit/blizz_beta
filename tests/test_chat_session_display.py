import types
import blizz_gui


class DummyWidget:
    def __init__(self):
        self.content = ""


def make_session():
    """Create a headless ChatSession wired to DummyWidgets."""
    s = object.__new__(blizz_gui.ChatSession)
    s.messages = []
    s.chat_log = DummyWidget()
    s.logic_box = DummyWidget()

    def append(widget, text):
        widget.content += text

    s._append_text = append  # type: ignore[attr-defined]
    s.render_to_top = types.MethodType(blizz_gui.ChatSession.render_to_top, s)
    s.render_to_bottom = types.MethodType(blizz_gui.ChatSession.render_to_bottom, s)
    s.render_message = types.MethodType(blizz_gui.ChatSession.render_message, s)
    s.update_displays = types.MethodType(blizz_gui.ChatSession.update_displays, s)
    s.parse_response = types.MethodType(blizz_gui.ChatSession.parse_response, s)
    s.structure_response = types.MethodType(blizz_gui.ChatSession.structure_response, s)
    return s


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
    chat, logic = session.structure_response({"user_facing_response": "hey", "bot_logic_output": "some reasoning"})
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


def test_instruction_prefix_routed_to_logic():
    session = make_session()
    instr = "Bot: The main bot should respond kindly"
    chat, logic = session.parse_response(instr)
    assert chat == ""
    assert logic == instr


def test_instruction_prefix_extended_pattern():
    session = make_session()
    instr = "Bot: The main bot should address the user"
    chat, logic = session.parse_response(instr)
    assert chat == ""
    assert logic == instr
