import json
import types

import modules.self_awareness as self_awareness
import modules.chat_handler as chat_handler


def test_load_features(tmp_path, monkeypatch):
    f = tmp_path / "features.json"
    f.write_text(json.dumps({"features": ["a", "b"]}))
    monkeypatch.setattr(self_awareness, "FEATURES_FILE", str(f))
    feats = self_awareness.load_features()
    assert feats == ["a", "b"]
    out = self_awareness.describe_features()
    assert "- a" in out and "- b" in out


def test_contextual_response_features(monkeypatch, tmp_path):
    f = tmp_path / "features.json"
    f.write_text(json.dumps({"features": ["exec", "scan"]}))
    monkeypatch.setattr(self_awareness, "FEATURES_FILE", str(f))
    monkeypatch.setattr(chat_handler, "load_neocortex_config", lambda: {"memory_retrieval": {"recent_limit": 5}})
    monkeypatch.setattr(chat_handler.context, "get_history", lambda limit: [])
    monkeypatch.setattr(chat_handler, "retrieve_processed_memory", lambda: {"conversation_history": []})

    resp = chat_handler.generate_contextual_response("What can you do?")
    assert "exec" in resp and "scan" in resp
