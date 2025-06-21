import json
import models.custom_memory as custom_memory


def test_save_context_respects_limit_list(monkeypatch, tmp_path):
    mem_file = tmp_path / "memory.json"
    memory = custom_memory.CustomMemory(memory_file=str(mem_file))
    monkeypatch.setattr(custom_memory, "load_neocortex_config", lambda: {"memory_limit": 3})

    for i in range(5):
        memory.save_context(f"u{i}", f"b{i}")

    with open(mem_file) as f:
        data = json.load(f)

    assert len(data) == 3
    assert [entry["user"] for entry in data] == ["u2", "u3", "u4"]


def test_save_context_respects_limit_dict(monkeypatch, tmp_path):
    mem_file = tmp_path / "memory.json"
    mem_file.write_text(json.dumps({"conversation_history": []}))
    memory = custom_memory.CustomMemory(memory_file=str(mem_file))
    monkeypatch.setattr(custom_memory, "load_neocortex_config", lambda: {"memory_limit": 2})

    for i in range(4):
        memory.save_context(f"user{i}", f"bot{i}")

    with open(mem_file) as f:
        data = json.load(f)

    assert list(data)
    history = data["conversation_history"]
    assert len(history) == 2
    assert [msg["user"] for msg in history] == ["user2", "user3"]
