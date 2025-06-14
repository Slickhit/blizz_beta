import modules.context as context
import modules.chat_handler as chat_handler


def test_context_timestamp_reset():
    context.set_last("pwd", "/home/user")
    _, _, ts1 = context.get_last()
    assert isinstance(ts1, float)

    context.set_last(None, None)
    _, _, ts2 = context.get_last()
    assert ts2 is None


def test_generate_contextual_response_generic():
    context.set_last("echo", "hello world")
    resp = chat_handler.generate_contextual_response("what was the output?")
    assert resp == "hello world"


def test_generate_contextual_response_none():
    context.set_last(None, None)
    resp = chat_handler.generate_contextual_response("where am i?")
    assert resp is None
