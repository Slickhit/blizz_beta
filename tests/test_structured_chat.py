import types
import modules.chat_handler as chat_handler


def test_handle_user_input_parses_json(monkeypatch):
    monkeypatch.setattr(chat_handler, "load_neocortex_config", lambda: {})

    class FakeModel:
        def invoke(self, prompt):
            return types.SimpleNamespace(content='{"final_response": "hi", "thought_process": "tp"}')

    monkeypatch.setattr(chat_handler, "main_bot", FakeModel())
    monkeypatch.setattr(chat_handler, "retrieve_processed_memory", lambda: {"conversation_history": []})
    monkeypatch.setattr(chat_handler, "neuron_advice", lambda *a, **k: "")
    monkeypatch.setattr(chat_handler, "memory", types.SimpleNamespace(save_context=lambda *a, **k: None))
    monkeypatch.setattr(chat_handler.event_logger, "log_event", lambda *a, **k: None)
    monkeypatch.setattr(chat_handler.memory_cache, "add_message", lambda *a, **k: None)
    monkeypatch.setattr(chat_handler.summarizer, "summarize_and_store", lambda *a, **k: None)

    result = chat_handler.handle_user_input("hello")
    assert result["final_response"] == "hi"
    assert result["thought_process"] == "tp"

