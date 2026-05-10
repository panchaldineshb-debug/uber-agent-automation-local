import pytest
from unittest.mock import patch, MagicMock, call


def test_mac_notifier_calls_osascript():
    from skills.notifier.mac_alert import MacNotifier

    with patch("skills.notifier.mac_alert.subprocess.run") as mock_run:
        MacNotifier.notify_admin("SarabiLabs", "Test message")

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "osascript" in args
    assert "Test message" in args[-1]
    assert "SarabiLabs" in args[-1]


def test_sms_notifier_sends_with_valid_credentials():
    from skills.notifier.handler import sms_notifier

    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(sid="SM123")

    with patch("keyring.get_password", side_effect=lambda s, k: {
        "twilio_sid": "ACfake",
        "twilio_token": "fake_token",
        "twilio_phone": "+15550001111",
    }.get(k)):
        with patch("skills.notifier.handler.Client", return_value=mock_client):
            result = sms_notifier.send_confirmation("+18483099176", "Ride booked for 4:00 PM")

    mock_client.messages.create.assert_called_once_with(
        body="Ride booked for 4:00 PM",
        from_="+15550001111",
        to="+18483099176",
    )
    assert result == "SM123"


def test_sms_notifier_raises_when_credentials_missing():
    from skills.notifier.handler import sms_notifier
    import pytest

    with patch("keyring.get_password", return_value=None):
        with pytest.raises(RuntimeError, match="Twilio credentials missing"):
            sms_notifier.send_confirmation("+18483099176", "Test")
