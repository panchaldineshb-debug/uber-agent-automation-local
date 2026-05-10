import pytest
from datetime import datetime
from skills.email_parser.handler import EmailParser


def test_extract_time_hour_and_minutes_pm():
    result = EmailParser.extract_time("I need a ride at 2:35 PM")
    assert result is not None
    assert result.hour == 14
    assert result.minute == 35


def test_extract_time_bare_hour_pm():
    result = EmailParser.extract_time("pick me up at 4 PM")
    assert result is not None
    assert result.hour == 16
    assert result.minute == 0


def test_extract_time_lowercase_pm():
    result = EmailParser.extract_time("ride at 4 pm please")
    assert result is not None
    assert result.hour == 16
    assert result.minute == 0


def test_extract_time_noon():
    result = EmailParser.extract_time("pickup at 12 PM")
    assert result is not None
    assert result.hour == 12
    assert result.minute == 0


def test_extract_time_midnight():
    result = EmailParser.extract_time("pickup at 12 AM")
    assert result is not None
    assert result.hour == 0
    assert result.minute == 0


def test_extract_time_no_time_returns_none():
    result = EmailParser.extract_time("hey can you book me a ride today?")
    assert result is None


def test_extract_time_returns_today():
    result = EmailParser.extract_time("ride at 4 PM")
    today = datetime.now().date()
    assert result.date() == today


def test_extract_time_235_pm():
    result = EmailParser.extract_time("2:35 PM pickup")
    assert result.hour == 14
    assert result.minute == 35
