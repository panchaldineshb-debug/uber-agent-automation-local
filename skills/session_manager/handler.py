import asyncio
import os
from datetime import datetime

from scripts.check_session import is_session_valid

STATE_PATH = "config/uber_state.json"
MAX_SESSION_AGE_DAYS = 7


class SessionManager:
    def state_path(self) -> str:
        return STATE_PATH

    def is_valid(self) -> bool:
        return asyncio.run(is_session_valid(STATE_PATH))

    def refresh_needed(self) -> bool:
        if not os.path.exists(STATE_PATH):
            return True
        age_days = (datetime.now().timestamp() - os.stat(STATE_PATH).st_mtime) / 86400
        return age_days >= MAX_SESSION_AGE_DAYS
