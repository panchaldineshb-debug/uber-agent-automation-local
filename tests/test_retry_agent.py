from unittest.mock import MagicMock, call, patch
import pytest
from agents.retry_agent import RetryAgent


@patch("agents.retry_agent.time.sleep")
def test_success_first_attempt(mock_sleep):
    fn = MagicMock(return_value="ok")
    result = RetryAgent().run_with_retry(fn, max_attempts=3, delay_seconds=5.0)
    assert result == "ok"
    fn.assert_called_once()
    mock_sleep.assert_not_called()


@patch("agents.retry_agent.time.sleep")
def test_success_on_third_attempt(mock_sleep):
    fn = MagicMock(side_effect=[Exception("fail"), Exception("fail"), "ok"])
    result = RetryAgent().run_with_retry(fn, max_attempts=3, delay_seconds=5.0)
    assert result == "ok"
    assert fn.call_count == 3


@patch("agents.retry_agent.time.sleep")
def test_all_attempts_fail_raises(mock_sleep):
    fn = MagicMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError, match="boom"):
        RetryAgent().run_with_retry(fn, max_attempts=3, delay_seconds=5.0)
    assert fn.call_count == 3


@patch("agents.retry_agent.time.sleep")
def test_exponential_backoff(mock_sleep):
    fn = MagicMock(side_effect=Exception("fail"))
    with pytest.raises(Exception):
        RetryAgent().run_with_retry(fn, max_attempts=3, delay_seconds=5.0)
    assert mock_sleep.call_args_list == [call(5.0), call(10.0), call(20.0)]


@patch("agents.retry_agent.time.sleep")
def test_run_ride_booking_success(mock_sleep):
    skill = MagicMock()
    skill.request_ride.return_value = True
    result = RetryAgent().run_ride_booking(skill, "2:35 PM", 40.5482, -74.3444)
    assert result is True


@patch("agents.retry_agent.time.sleep")
def test_run_ride_booking_all_fail(mock_sleep):
    skill = MagicMock()
    skill.request_ride.side_effect = Exception("network error")
    result = RetryAgent().run_ride_booking(skill, "2:35 PM", 40.5482, -74.3444, max_attempts=3)
    assert result is False
