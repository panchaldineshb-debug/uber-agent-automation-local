import pytest
from unittest.mock import patch, MagicMock, call


def test_send_failure_email_raises_without_keychain():
    from skills.notifier.email_client import send_failure_email

    with patch("keyring.get_password", return_value=None):
        with pytest.raises(RuntimeError, match="gmail_app_password"):
            send_failure_email("something failed", "poll_gmail")


def test_send_failure_email_sends_to_both_recipients():
    from skills.notifier import email_client

    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("keyring.get_password", return_value="app-password"):
        with patch("skills.notifier.email_client.smtplib.SMTP_SSL", return_value=mock_smtp):
            email_client.send_failure_email("crash details", "poll_gmail")

    assert mock_server.sendmail.call_count == 2
    recipients = [c[0][1] for c in mock_server.sendmail.call_args_list]
    assert email_client.ADMIN_EMAIL in recipients
    assert str(email_client.settings.SON_EMAIL) in recipients


def test_send_failure_email_sameer_body_has_action():
    from skills.notifier import email_client

    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("keyring.get_password", return_value="app-password"):
        with patch("skills.notifier.email_client.smtplib.SMTP_SSL", return_func=mock_smtp):
            with patch("skills.notifier.email_client._send_email") as mock_send:
                email_client.send_failure_email("crash details", "poll_gmail")

    calls = mock_send.call_args_list
    sameer_call = next(c for c in calls if str(email_client.settings.SON_EMAIL) in c[0][0])
    assert "Call Dad" in sameer_call[0][2]


def test_send_failure_email_admin_body_has_error_details():
    from skills.notifier import email_client

    with patch("skills.notifier.email_client._send_email") as mock_send:
        email_client.send_failure_email("NullPointerException at line 42", "process_ride_intent")

    calls = mock_send.call_args_list
    admin_call = next(c for c in calls if email_client.ADMIN_EMAIL in c[0][0])
    assert "NullPointerException at line 42" in admin_call[0][2]
    assert "process_ride_intent" in admin_call[0][2]
