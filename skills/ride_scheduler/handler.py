from datetime import datetime, timedelta
import pytz

EST = pytz.timezone("America/New_York")
_SLOTS = [(14, 35), (16, 0)]
_WINDOW_MINUTES = 10


class RideScheduler:
    def is_allowed_time(self, ride_time: datetime) -> bool:
        if ride_time.tzinfo is None:
            ride_time = EST.localize(ride_time)
        est_time = ride_time.astimezone(EST)
        for hour, minute in _SLOTS:
            slot = est_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if abs((est_time - slot).total_seconds()) <= _WINDOW_MINUTES * 60:
                return True
        return False

    def next_allowed_slot(self, now: datetime | None = None) -> datetime:
        if now is None:
            now = datetime.now(EST)
        if now.tzinfo is None:
            now = EST.localize(now)
        now = now.astimezone(EST)
        for hour, minute in _SLOTS:
            slot = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if slot > now:
                return slot
        tomorrow = (now + timedelta(days=1)).replace(
            hour=_SLOTS[0][0], minute=_SLOTS[0][1], second=0, microsecond=0
        )
        return tomorrow

    def format_slot(self, dt: datetime) -> str:
        est = dt.astimezone(EST)
        return est.strftime("%-I:%M %p")
