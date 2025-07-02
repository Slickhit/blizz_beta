import modules.summarizer as summarizer


def test_summarize_text_fallback(monkeypatch):
    # Force import error for transformers
    monkeypatch.setitem(__import__('sys').modules, 'transformers', None)
    text = 'hello world'
    assert summarizer.summarize_text(text, max_length=20) == text
