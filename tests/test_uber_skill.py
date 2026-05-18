import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime


def test_request_ride_raises_when_home_address_missing():
    with patch("keyring.get_password", return_value=None):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()
        with pytest.raises(RuntimeError, match="home_address"):
            skill.request_ride(datetime.now(), 40.5482, -74.3444)


def test_request_ride_returns_true_on_success():
    with patch("keyring.get_password", return_value="123 Home St, Edison NJ"):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()

    with patch("skills.ride_request.handler._book_ride_async", new=AsyncMock(return_value=True)):
        result = skill.request_ride(datetime.now(), 40.5482, -74.3444)

    assert result is True


def test_request_ride_returns_false_on_failure():
    with patch("keyring.get_password", return_value="123 Home St, Edison NJ"):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()

    with patch("skills.ride_request.handler._book_ride_async", new=AsyncMock(return_value=False)):
        result = skill.request_ride(datetime.now(), 40.5482, -74.3444)

    assert result is False


def test_request_ride_uses_state_path():
    with patch("keyring.get_password", return_value="123 Home St, Edison NJ"):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()

    with patch("skills.ride_request.handler._book_ride_async", new=AsyncMock(return_value=True)) as mock_fn:
        skill.request_ride(datetime.now(), 40.5482, -74.3444)

    assert mock_fn.called
