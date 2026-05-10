import email
import email.header
import pytest
from unittest.mock import patch, MagicMock


def _decode_sent_message(mock_server):
    raw = mock_server.sendmail.call_args[0][2]
    msg = email.message_from_string(raw)
    # Decode RFC 2047 encoded subject (e.g. =?utf-8?q?...?=)
    subject_parts = email.header.decode_header(msg["Subject"])
    subject = "".join(
        part.decode(enc or "utf-8") if isinstance(part, bytes) else part
        for part, enc in subject_parts
    )
    body = ""
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode()
    return subject, body


def test_send_confirmation_raises_without_keychain():
    from skills.email_reply.handler import send_confirmation

    with patch("keyring.get_password", return_value=None):
        with pytest.raises(RuntimeError, match="Gmail app password"):
            send_confirmation("sameer@test.com", "4:00 PM")


def test_send_confirmation_sends_correct_subject():
    from skills.email_reply.handler import send_confirmation

    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("keyring.get_password", return_value="app-password"):
        with patch("skills.email_reply.handler.smtplib.SMTP_SSL", return_value=mock_smtp):
            send_confirmation("sameer@test.com", "4:00 PM")

    subject, body = _decode_sent_message(mock_server)
    assert "4:00 PM" in subject
    assert "Uber Confirmed" in subject


def test_send_confirmation_includes_driver_info():
    from skills.email_reply.handler import send_confirmation

    mock_server = MagicMock()
    mock_smtp = MagicMock()
    mock_smtp.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp.__exit__ = MagicMock(return_value=False)

    with patch("keyring.get_password", return_value="app-password"):
        with patch("skills.email_reply.handler.smtplib.SMTP_SSL", return_value=mock_smtp):
            send_confirmation("sameer@test.com", "2:35 PM")

    subject, body = _decode_sent_message(mock_server)
    assert "Driver" in body
    assert "Vehicle" in body
    assert "License" in body
