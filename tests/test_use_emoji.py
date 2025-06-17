import types
import modules.chat_handler as chat_handler


def test_handle_user_input_appends_emoji(monkeypatch):
    # config with emoji enabled
    monkeypatch.setattr(chat_handler, "load_neocortex_config", lambda: {"use_emoji": True})

    class FakeModel:
        def invoke(self, prompt):
            return types.SimpleNamespace(content="hello")

    monkeypatch.setattr(chat_handler, "main_bot", FakeModel())
    monkeypatch.setattr(chat_handler, "retrieve_processed_memory", lambda: {"conversation_history": []})
    monkeypatch.setattr(chat_handler, "neuron_advice", lambda *args, **kwargs: "")
    monkeypatch.setattr(chat_handler, "memory", types.SimpleNamespace(save_context=lambda *a, **k: None))
    monkeypatch.setattr(chat_handler.event_logger, "log_event", lambda *a, **k: None)

    result = chat_handler.handle_user_input("hi")
    assert "hello" in result
    assert "😊" in result
