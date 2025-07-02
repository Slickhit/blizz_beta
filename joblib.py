"""Minimal joblib replacement for tests."""

import pickle
from typing import Any


def dump(obj: Any, filename: str) -> None:
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def load(filename: str) -> Any:
    with open(filename, "rb") as f:
        return pickle.load(f)

