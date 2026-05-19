import json
import pytest
from datetime import date
from pathlib import Path
from skills.rate_limiter.handler import RateLimiter


@pytest.fixture
def rl(tmp_path):
    state_file = tmp_path / "ride_count.json"
    return RateLimiter(state_path=state_file)


def test_fresh_state_can_book(rl):
    assert rl.can_book() is True
    assert rl.today_count() == 0


def test_one_booking_still_allowed(rl):
    rl.record_booking()
    assert rl.can_book() is True
    assert rl.today_count() == 1


def test_two_bookings_blocked(rl):
    rl.record_booking()
    rl.record_booking()
    assert rl.can_book() is False
    assert rl.today_count() == 2


def test_reset_clears_count(rl):
    rl.record_booking()
    rl.record_booking()
    rl.reset()
    assert rl.can_book() is True
    assert rl.today_count() == 0


def test_date_rollover_resets_count(rl, tmp_path):
    yesterday = (date.today().replace(day=date.today().day - 1) if date.today().day > 1
                 else date(date.today().year, date.today().month - 1, 28)).isoformat()
    state_file = tmp_path / "ride_count.json"
    state_file.write_text(json.dumps({"date": yesterday, "count": 2}))
    rl2 = RateLimiter(state_path=state_file)
    assert rl2.can_book() is True
    assert rl2.today_count() == 0
