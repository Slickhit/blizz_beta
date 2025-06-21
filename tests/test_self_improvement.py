import os
import types
import modules.self_improvement as self_improvement


def test_self_improve_creates_log(monkeypatch):
    monkeypatch.setattr(self_improvement, "read_own_code", lambda fp: "print('hi')")
    monkeypatch.setattr(self_improvement, "modify_own_code", lambda fp, code: "ok")

    class DummyModel:
        def invoke(self, prompt):
            return types.SimpleNamespace(content="print('improved')")

    monkeypatch.setattr(self_improvement, "model", DummyModel())

    log_dir = os.path.join(os.path.dirname(self_improvement.__file__), "logs")
    log_path = os.path.join(log_dir, "ai_generated_code.py")
    if os.path.exists(log_path):
        os.remove(log_path)

    result = self_improvement.self_improve_code("dummy.py")

    assert result == "ok"
    assert os.path.exists(log_path)
    os.remove(log_path)
