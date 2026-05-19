import json
import time
from unittest.mock import MagicMock, mock_open, patch
from agents.session_agent import SessionAgent


def test_is_valid_missing_file():
    with patch("agents.session_agent.os.path.exists", return_value=False):
        assert SessionAgent().is_valid() is False


def test_is_valid_fresh_file():
    stat_mock = MagicMock(st_mtime=time.time() - 3600)
    with patch("agents.session_agent.os.path.exists", return_value=True), \
         patch("agents.session_agent.os.stat", return_value=stat_mock):
        assert SessionAgent().is_valid() is True


def test_is_valid_old_file():
    stat_mock = MagicMock(st_mtime=time.time() - 8 * 86400)
    with patch("agents.session_agent.os.path.exists", return_value=True), \
         patch("agents.session_agent.os.stat", return_value=stat_mock):
        assert SessionAgent().is_valid() is False


def test_load_state_valid_json():
    payload = json.dumps({"cookies": []})
    with patch("builtins.open", mock_open(read_data=payload)):
        result = SessionAgent().load_state()
    assert result == {"cookies": []}


def test_load_state_missing_file():
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert SessionAgent().load_state() == {}


def test_load_state_corrupt_json():
    with patch("builtins.open", mock_open(read_data="not json")):
        assert SessionAgent().load_state() == {}


def test_session_age_hours_missing():
    with patch("agents.session_agent.os.path.exists", return_value=False):
        assert SessionAgent().session_age_hours() == float("inf")


def test_session_age_hours_recent():
    stat_mock = MagicMock(st_mtime=time.time() - 7200)
    with patch("agents.session_agent.os.path.exists", return_value=True), \
         patch("agents.session_agent.os.stat", return_value=stat_mock):
        age = SessionAgent().session_age_hours()
    assert 1.9 < age < 2.1


def test_needs_refresh_valid():
    sa = SessionAgent()
    with patch.object(sa, "is_valid", return_value=True):
        assert sa.needs_refresh() is False


def test_needs_refresh_invalid():
    sa = SessionAgent()
    with patch.object(sa, "is_valid", return_value=False):
        assert sa.needs_refresh() is True
