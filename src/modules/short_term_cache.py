from typing import List, Dict

from models.custom_memory import CustomMemory

class ShortTermMemoryCache:
    """Ephemeral in-process cache for recent messages."""

    def __init__(self, limit: int = 5, store: CustomMemory | None = None) -> None:
        self.limit = limit
        self.store = store or CustomMemory()
        self._buffer: List[Dict[str, str]] = []

    def add_message(self, user: str, bot: str) -> None:
        self._buffer.append({"user": user, "bot": bot})
        if len(self._buffer) >= self.limit:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return
        for entry in self._buffer:
            self.store.save_context(entry["user"], entry["bot"])
        self._buffer.clear()

cache = ShortTermMemoryCache()
