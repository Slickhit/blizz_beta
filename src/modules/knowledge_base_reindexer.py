"""Re-embed knowledge sources whenever files change."""

import os
from modules import summarizer


def reindex_directory(path: str) -> None:
    for root, _dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                summarizer.summarize_and_store("kb", content)
            except Exception:
                pass

