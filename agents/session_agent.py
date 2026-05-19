import json
import os
from datetime import datetime

from core import logger

STATE_PATH = "config/uber_state.json"
MAX_SESSION_AGE_DAYS = 7


class SessionAgent:
    def get_state_path(self) -> str:
        return STATE_PATH

    def is_valid(self) -> bool:
        if not os.path.exists(STATE_PATH):
            return False
        try:
            age_days = (datetime.now().timestamp() - os.stat(STATE_PATH).st_mtime) / 86400
            return age_days < MAX_SESSION_AGE_DAYS
        except OSError:
            return False

    def load_state(self) -> dict:
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"[session] could not load state: {e}")
            return {}

    def session_age_hours(self) -> float:
        if not os.path.exists(STATE_PATH):
            return float("inf")
        try:
            age_secs = datetime.now().timestamp() - os.stat(STATE_PATH).st_mtime
            return age_secs / 3600
        except OSError:
            return float("inf")

    def needs_refresh(self) -> bool:
        return not self.is_valid()
