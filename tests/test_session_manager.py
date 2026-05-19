import time
from unittest.mock import MagicMock, patch
from skills.session_manager.handler import SessionManager


def test_is_valid_true():
    with patch("skills.session_manager.handler.asyncio.run", return_value=True):
        assert SessionManager().is_valid() is True


def test_is_valid_false():
    with patch("skills.session_manager.handler.asyncio.run", return_value=False):
        assert SessionManager().is_valid() is False


def test_refresh_needed_missing_file():
    with patch("skills.session_manager.handler.os.path.exists", return_value=False):
        assert SessionManager().refresh_needed() is True


def test_refresh_needed_old_file():
    old_mtime = time.time() - (8 * 86400)
    stat_mock = MagicMock()
    stat_mock.st_mtime = old_mtime
    with patch("skills.session_manager.handler.os.path.exists", return_value=True), \
         patch("skills.session_manager.handler.os.stat", return_value=stat_mock):
        assert SessionManager().refresh_needed() is True


def test_refresh_needed_fresh_file():
    stat_mock = MagicMock()
    stat_mock.st_mtime = time.time() - 3600
    with patch("skills.session_manager.handler.os.path.exists", return_value=True), \
         patch("skills.session_manager.handler.os.stat", return_value=stat_mock):
        assert SessionManager().refresh_needed() is False


def test_state_path():
    assert SessionManager().state_path() == "config/uber_state.json"
