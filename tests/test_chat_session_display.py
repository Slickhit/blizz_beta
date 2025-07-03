import types
from blizz_gui import ChatSession


class DummyWidget:
    def __init__(self):
        self.content = ""


def make_session():
    s = object.__new__(ChatSession)
    s.messages = []
    s.chat_log = DummyWidget()
    s.logic_box = DummyWidget()

    def append(widget, text):
        widget.content += text

    s._append_text = append
    s.render_to_top = types.MethodType(ChatSession.render_to_top, s)
    s.render_to_bottom = types.MethodType(ChatSession.render_to_bottom, s)
    s.render_message = types.MethodType(ChatSession.render_message, s)
    s.update_displays = types.MethodType(ChatSession.update_displays, s)
    s.parse_response = types.MethodType(ChatSession.parse_response, s)
    s.structure_response = types.MethodType(ChatSession.structure_response, s)
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
