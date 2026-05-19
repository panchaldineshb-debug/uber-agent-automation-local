import time
from unittest.mock import MagicMock, patch
from agents.health_monitor import HealthMonitor


def test_check_launchd_running():
    result_mock = MagicMock(returncode=0, stdout="PID = 1234\n")
    with patch("agents.health_monitor.subprocess.run", return_value=result_mock):
        assert HealthMonitor().check_launchd() is True


def test_check_launchd_not_running():
    result_mock = MagicMock(returncode=1, stdout="")
    with patch("agents.health_monitor.subprocess.run", return_value=result_mock):
        assert HealthMonitor().check_launchd() is False


def test_check_launchd_exception():
    with patch("agents.health_monitor.subprocess.run", side_effect=OSError("no launchctl")):
        assert HealthMonitor().check_launchd() is False


def test_check_session_fresh_missing():
    with patch("agents.health_monitor.os.path.exists", return_value=False):
        assert HealthMonitor().check_session_fresh() is False


def test_check_session_fresh_recent():
    stat_mock = MagicMock(st_mtime=time.time() - 3600)
    with patch("agents.health_monitor.os.path.exists", return_value=True), \
         patch("agents.health_monitor.os.stat", return_value=stat_mock):
        assert HealthMonitor().check_session_fresh() is True


def test_check_session_fresh_old():
    stat_mock = MagicMock(st_mtime=time.time() - 8 * 86400)
    with patch("agents.health_monitor.os.path.exists", return_value=True), \
         patch("agents.health_monitor.os.stat", return_value=stat_mock):
        assert HealthMonitor().check_session_fresh() is False


def test_check_disk_space_ok():
    usage_mock = MagicMock(used=100 * 1024 * 1024)
    with patch("agents.health_monitor.Path.exists", return_value=True), \
         patch("agents.health_monitor.shutil.disk_usage", return_value=usage_mock):
        assert HealthMonitor().check_disk_space() is True


def test_check_disk_space_full():
    usage_mock = MagicMock(used=600 * 1024 * 1024)
    with patch("agents.health_monitor.Path.exists", return_value=True), \
         patch("agents.health_monitor.shutil.disk_usage", return_value=usage_mock):
        assert HealthMonitor().check_disk_space() is False


def test_run_all_healthy():
    hm = HealthMonitor()
    with patch.object(hm, "check_launchd", return_value=True), \
         patch.object(hm, "check_session_fresh", return_value=True), \
         patch.object(hm, "check_disk_space", return_value=True):
        result = hm.run_all()
    assert result == {"launchd": True, "session": True, "disk": True, "healthy": True}


def test_run_all_unhealthy():
    hm = HealthMonitor()
    with patch.object(hm, "check_launchd", return_value=False), \
         patch.object(hm, "check_session_fresh", return_value=True), \
         patch.object(hm, "check_disk_space", return_value=True):
        result = hm.run_all()
    assert result["healthy"] is False
