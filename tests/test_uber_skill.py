import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


def test_uber_skill_raises_when_token_missing():
    with patch("keyring.get_password", return_value=None):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        with pytest.raises(RuntimeError, match="uber_server_token"):
            mod.UberSkill()


def test_request_ride_success():
    with patch("keyring.get_password", return_value="fake-token"):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()

    mock_response = MagicMock()
    mock_response.status_code = 201

    with patch("skills.ride_request.handler.requests.post", return_value=mock_response):
        result = skill.request_ride(datetime.now(), 40.5482, -74.3444)

    assert result is True


def test_request_ride_failure():
    with patch("keyring.get_password", return_value="fake-token"):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch("skills.ride_request.handler.requests.post", return_value=mock_response):
        result = skill.request_ride(datetime.now(), 40.5482, -74.3444)

    assert result is False


def test_request_ride_sends_correct_coordinates():
    with patch("keyring.get_password", return_value="fake-token"):
        from importlib import reload
        import skills.ride_request.handler as mod
        reload(mod)
        skill = mod.UberSkill()

    mock_response = MagicMock()
    mock_response.status_code = 201

    with patch("skills.ride_request.handler.requests.post", return_value=mock_response) as mock_post:
        skill.request_ride(datetime.now(), 40.5482, -74.3444)

    payload = mock_post.call_args[1]["json"]
    assert payload["start_latitude"] == 40.5482
    assert payload["start_longitude"] == -74.3444
