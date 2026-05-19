import time
from typing import Any, Callable

from core import logger

MAX_DELAY = 60.0


class RetryAgent:
    def run_with_retry(
        self,
        fn: Callable,
        max_attempts: int = 3,
        delay_seconds: float = 5.0,
    ) -> Any:
        last_exc: Exception | None = None
        for attempt in range(max_attempts):
            try:
                return fn()
            except Exception as e:
                last_exc = e
                wait = min(delay_seconds * (2 ** attempt), MAX_DELAY)
                logger.warning(f"[retry] attempt {attempt + 1}/{max_attempts} failed: {e}. Waiting {wait}s")
                time.sleep(wait)
        raise last_exc  # type: ignore[misc]

    def run_ride_booking(
        self,
        uber_skill,
        ride_time,
        pickup_lat: float,
        pickup_lon: float,
        max_attempts: int = 3,
    ) -> bool:
        try:
            self.run_with_retry(
                lambda: uber_skill.request_ride(ride_time, pickup_lat, pickup_lon),
                max_attempts=max_attempts,
            )
            return True
        except Exception as e:
            logger.error(f"[retry] all {max_attempts} booking attempts failed: {e}")
            return False
