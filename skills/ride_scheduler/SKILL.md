## Purpose
Validate that a requested ride time falls within an allowed pickup window.
Allowed slots: 2:35 PM EST and 4:00 PM EST (±10 minutes each).

## Inputs
- `ride_time: datetime` — naive (assumed EST) or tz-aware

## Outputs
- `is_allowed_time(dt) -> bool`
- `next_allowed_slot(now=None) -> datetime` — next upcoming slot from now
- `format_slot(dt) -> str` — e.g. "2:35 PM"

## Dependencies
- `pytz` (already in pyproject.toml via geopy transitive dep)

## Public API
```python
from skills.ride_scheduler.handler import RideScheduler

rs = RideScheduler()
rs.is_allowed_time(ride_time)        # -> bool
rs.next_allowed_slot()               # -> datetime (EST, tz-aware)
rs.format_slot(dt)                   # -> "2:35 PM"
```
