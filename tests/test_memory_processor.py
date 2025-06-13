import json
from types import SimpleNamespace
import os

import pytest

import modules.memory_processor as memory_processor

class FakeMemory:
    def __init__(self, data):
        self._data = data

    def load_memory(self):
        return self._data


def make_fake_model(response_content):
    class FakeModel:
        def invoke(self, prompt):
            return SimpleNamespace(content=response_content)
    return FakeModel()


def run_process_memory(monkeypatch, tmp_path, raw_memory, model_response):
    fake_memory = FakeMemory(raw_memory)
    monkeypatch.setattr(memory_processor, "memory", fake_memory)
    monkeypatch.setattr(memory_processor, "processing_bot", make_fake_model(model_response))

    processed_file = tmp_path / "processed.json"
    monkeypatch.setattr(memory_processor, "PROCESSED_MEMORY_FILE", str(processed_file))

    memory_processor.process_memory()
    with open(processed_file) as f:
        return json.load(f)


def test_process_memory_valid(monkeypatch, tmp_path):
    raw = {
        "conversation_history": [{"user": "hi", "bot": "hello"}],
        "preferences": {"color": "blue"}
    }
    data = run_process_memory(monkeypatch, tmp_path, raw, '{"personal_data": {"name": "Alice"}}')
    assert data["personal_data"]["name"] == "Alice"
    assert data["preferences"] == {"color": "blue"}
    assert data["conversation_history"] == [{"user": "hi", "bot": "hello"}]


def test_process_memory_invalid_json(monkeypatch, tmp_path):
    raw = {
        "conversation_history": [{"user": "hi", "bot": "hello"}],
    }
    data = run_process_memory(monkeypatch, tmp_path, raw, 'not json')
    assert data["personal_data"] == {}
    assert data["conversation_history"] == [{"user": "hi", "bot": "hello"}]
