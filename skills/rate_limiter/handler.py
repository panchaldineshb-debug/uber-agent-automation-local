import json
import os
from datetime import date
from pathlib import Path

from core.settings import settings

_STATE_FILE = settings.UBER_STATE_FILE.parent / "ride_count.json"


def _load(path: Path = _STATE_FILE) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(state: dict, path: Path = _STATE_FILE) -> None:
    with open(path, "w") as f:
        json.dump(state, f)


class RateLimiter:
    def __init__(self, state_path: Path = _STATE_FILE):
        self._path = state_path

    def _today(self) -> str:
        return date.today().isoformat()

    def _current(self) -> dict:
        state = _load(self._path)
        if state.get("date") != self._today():
            return {"date": self._today(), "count": 0}
        return state

    def today_count(self) -> int:
        return self._current().get("count", 0)

    def can_book(self) -> bool:
        return self.today_count() < 2

    def record_booking(self) -> None:
        state = self._current()
        state["count"] = state.get("count", 0) + 1
        _save(state, self._path)

    def reset(self) -> None:
        _save({"date": self._today(), "count": 0}, self._path)
