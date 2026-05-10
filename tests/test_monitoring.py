import pytest
from unittest.mock import patch, MagicMock
from core.monitoring import sarabilabs_monitor


def test_decorator_passes_return_value():
    @sarabilabs_monitor
    def good_func():
        return 42

    assert good_func() == 42


def test_decorator_returns_none_on_exception():
    @sarabilabs_monitor
    def bad_func():
        raise ValueError("boom")

    with patch("core.monitoring.send_failure_email"):
        result = bad_func()

    assert result is None


def test_decorator_calls_send_failure_email_on_exception():
    @sarabilabs_monitor
    def bad_func():
        raise RuntimeError("something broke")

    with patch("core.monitoring.send_failure_email") as mock_notify:
        bad_func()

    mock_notify.assert_called_once()
    args = mock_notify.call_args[0]
    assert "bad_func" in args[0]
    assert args[1] == "bad_func"


def test_decorator_survives_notify_failure():
    @sarabilabs_monitor
    def bad_func():
        raise RuntimeError("original error")

    with patch("core.monitoring.send_failure_email", side_effect=Exception("email down")):
        result = bad_func()

    assert result is None


def test_decorator_preserves_function_name():
    @sarabilabs_monitor
    def my_named_func():
        pass

    assert my_named_func.__name__ == "my_named_func"
