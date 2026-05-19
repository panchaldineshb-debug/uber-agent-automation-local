import pytz
from datetime import datetime
from skills.ride_scheduler.handler import RideScheduler

EST = pytz.timezone("America/New_York")


def _est(h, m):
    return EST.localize(datetime.now().replace(hour=h, minute=m, second=0, microsecond=0))


def test_235pm_allowed():
    assert RideScheduler().is_allowed_time(_est(14, 35)) is True


def test_400pm_allowed():
    assert RideScheduler().is_allowed_time(_est(16, 0)) is True


def test_within_window_235_allowed():
    assert RideScheduler().is_allowed_time(_est(14, 30)) is True


def test_outside_both_windows_rejected():
    assert RideScheduler().is_allowed_time(_est(15, 0)) is False


def test_next_slot_before_235_returns_235():
    now = _est(10, 0)
    slot = RideScheduler().next_allowed_slot(now)
    assert slot.hour == 14 and slot.minute == 35


def test_next_slot_between_235_and_400_returns_400():
    now = _est(14, 50)
    slot = RideScheduler().next_allowed_slot(now)
    assert slot.hour == 16 and slot.minute == 0


def test_next_slot_after_400_returns_next_day_235():
    now = _est(17, 0)
    slot = RideScheduler().next_allowed_slot(now)
    assert slot.hour == 14 and slot.minute == 35
    assert slot.date() > now.date()


def test_format_slot():
    dt = _est(14, 35)
    assert RideScheduler().format_slot(dt) == "2:35 PM"
