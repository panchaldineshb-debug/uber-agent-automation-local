## Purpose
Enforce max 2 Uber ride bookings per calendar day.

## Inputs
None — stateful via `config/ride_count.json`.

## Outputs
- `can_book() -> bool` — False if today's count >= 2
- `today_count() -> int` — bookings recorded today
- `record_booking() -> None` — increment count (call on confirmed success only)
- `reset() -> None` — reset count to 0 for today (ops/testing use)

## State File
`config/ride_count.json` — format: `{"date": "YYYY-MM-DD", "count": N}`
Date rollover is automatic: new day resets count to 0.

## Public API
```python
from skills.rate_limiter.handler import RateLimiter

rl = RateLimiter()
if rl.can_book():
    # book ride
    rl.record_booking()
```
