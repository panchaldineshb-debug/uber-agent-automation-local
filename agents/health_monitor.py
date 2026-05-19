import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from core import logger

STATE_PATH = "config/uber_state.json"
MAX_SESSION_AGE_DAYS = 7
MAX_LOG_MB = 500
LAUNCHD_LABEL = "com.sarabilabs.rideagent"


class HealthMonitor:
    def check_launchd(self) -> bool:
        try:
            result = subprocess.run(
                ["launchctl", "list", LAUNCHD_LABEL],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and "PID" in result.stdout
        except Exception as e:
            logger.warning(f"[health] launchd check failed: {e}")
            return False

    def check_session_fresh(self) -> bool:
        if not os.path.exists(STATE_PATH):
            return False
        try:
            age_days = (datetime.now().timestamp() - os.stat(STATE_PATH).st_mtime) / 86400
            return age_days < MAX_SESSION_AGE_DAYS
        except OSError:
            return False

    def check_disk_space(self) -> bool:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return True
        try:
            usage = shutil.disk_usage(logs_dir)
            used_mb = usage.used / (1024 * 1024)
            return used_mb < MAX_LOG_MB
        except OSError:
            return True

    def run_all(self) -> dict:
        results = {
            "launchd": self.check_launchd(),
            "session": self.check_session_fresh(),
            "disk": self.check_disk_space(),
        }
        results["healthy"] = all(results.values())
        return results
