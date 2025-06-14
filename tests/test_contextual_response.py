import modules.context as context
import modules.chat_handler as chat_handler


def test_generate_contextual_response_pwd():
    context.set_last("pwd", "/home/user")
    resp = chat_handler.generate_contextual_response("where am i in the directory?")
    assert "/home/user" in resp


def test_generate_contextual_response_generic():
    context.set_last("echo", "hello world")
    resp = chat_handler.generate_contextual_response("what was the output?")
    assert resp == "hello world"


def test_generate_contextual_response_none():
    context.set_last(None, None)
    resp = chat_handler.generate_contextual_response("where am i?")
    assert resp is None
