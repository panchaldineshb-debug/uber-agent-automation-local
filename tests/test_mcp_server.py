import json
import time
from unittest.mock import MagicMock, patch

from scripts.mcp_server import (
    check_uber_session,
    get_ride_count_today,
    check_launchd_service,
    get_agent_logs,
)


class TestCheckUberSession:
    def test_missing_file(self):
        with patch("scripts.mcp_server.os.stat") as mock_stat, \
             patch("scripts.mcp_server.Path.exists", return_value=False):
            result = check_uber_session()
        assert result == "expired: missing"

    def test_valid_fresh_file(self):
        stat_mock = MagicMock(st_mtime=time.time() - 86400)
        with patch("scripts.mcp_server.Path.exists", return_value=True), \
             patch("scripts.mcp_server.os.stat", return_value=stat_mock):
            result = check_uber_session()
        assert result == "valid"

    def test_expired_old_file(self):
        stat_mock = MagicMock(st_mtime=time.time() - 8 * 86400)
        with patch("scripts.mcp_server.Path.exists", return_value=True), \
             patch("scripts.mcp_server.os.stat", return_value=stat_mock):
            result = check_uber_session()
        assert result.startswith("expired: age:")


class TestGetRideCountToday:
    def test_missing_file(self):
        with patch("scripts.mcp_server.Path.exists", return_value=False):
            result = get_ride_count_today()
        assert result == "count: 0/2 (no state)"

    def test_valid_state_file(self):
        data = json.dumps({"count": 1, "date": "2026-05-18"})
        with patch("scripts.mcp_server.Path.exists", return_value=True), \
             patch("scripts.mcp_server.Path.read_text", return_value=data):
            result = get_ride_count_today()
        assert result == "count: 1/2 for 2026-05-18"


class TestCheckLaunchdService:
    def test_running(self):
        result_mock = MagicMock(returncode=0, stdout='{\n\t"PID" = 1234;\n}', stderr="")
        with patch("scripts.mcp_server.subprocess.run", return_value=result_mock):
            result = check_launchd_service()
        assert result == "running"

    def test_stopped(self):
        result_mock = MagicMock(returncode=1, stdout="", stderr="Could not find service")
        with patch("scripts.mcp_server.subprocess.run", return_value=result_mock):
            result = check_launchd_service()
        assert result.startswith("stopped:")


class TestGetAgentLogs:
    def test_file_missing(self):
        with patch("scripts.mcp_server.Path.exists", return_value=False):
            assert get_agent_logs() == "no logs"

    def test_returns_last_n_lines(self):
        content = "\n".join(f"line {i}" for i in range(1, 31))
        with patch("scripts.mcp_server.Path.exists", return_value=True), \
             patch("scripts.mcp_server.Path.read_text", return_value=content):
            result = get_agent_logs(lines=5)
        lines = result.splitlines()
        assert len(lines) == 5
        assert lines[-1] == "line 30"
