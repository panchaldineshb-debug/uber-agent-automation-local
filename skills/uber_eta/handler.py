import asyncio
from scripts.uber_eta import get_uber_eta


class UberETASkill:
    def get_eta(self, pickup: str, dropoff: str) -> list[dict]:
        try:
            results = asyncio.run(get_uber_eta(pickup, dropoff))
            return results if results else []
        except Exception:
            return []
