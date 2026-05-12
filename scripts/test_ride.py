"""
Live browser test for ride_request handler.
Uses today's date at 2:35 PM as pickup time.
UBER_HEADLESS=false and UBER_DRY_RUN=true are set by `make uber-test` — no real booking.
"""
import asyncio
from datetime import datetime
from skills.ride_request.handler import _book_ride_async, STATE_PATH, HEADLESS, DRY_RUN

pickup_time = datetime.now().replace(hour=14, minute=35, second=0, microsecond=0)

print(f"[TEST] headless={HEADLESS}  dry_run={DRY_RUN}  pickup={pickup_time.strftime('%-I:%M %p')}")

result = asyncio.run(_book_ride_async(pickup_time, STATE_PATH))
print(f"[TEST] result={result}")
