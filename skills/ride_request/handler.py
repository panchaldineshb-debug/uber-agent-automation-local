import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
import keyring

SERVICE_NAME = "SarabiLabs_Uber_Automator"
STATE_PATH = "config/uber_state.json"

# JP Stevens High School, Edison NJ
PICKUP_LAT = 40.5482
PICKUP_LON = -74.3444


def _get_home_address() -> str:
    addr = keyring.get_password(SERVICE_NAME, "home_address")
    if not addr:
        raise RuntimeError(
            "Keychain entry 'home_address' not found. Run 'make seed-secrets'."
        )
    return addr


async def _book_ride_async(pickup_time: datetime, state_path: str) -> bool:
    home_address = _get_home_address()
    time_label = pickup_time.strftime("%-I:%M %p")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state=state_path,
            # Spoof geolocation to JP Stevens so Uber auto-detects pickup
            geolocation={"latitude": PICKUP_LAT, "longitude": PICKUP_LON},
            permissions=["geolocation"],
        )
        page = await context.new_page()

        try:
            await page.goto("https://m.uber.com/looking", timeout=30000)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)

            # --- Step 1: Click the dropoff/destination input ---
            # Uber mobile web uses "Dropoff location" or "Where are you going?"
            dest_input = page.locator(
                "input[placeholder*='Dropoff'], "
                "input[placeholder*='Where are you going'], "
                "input[placeholder*='Destination'], "
                "input[placeholder*='Where to']"
            ).first
            if not await dest_input.is_visible(timeout=4000):
                # Fallback: click the visible "Get a ride" button first, then find input
                get_ride = page.get_by_text("Get a ride", exact=False)
                if await get_ride.is_visible(timeout=3000):
                    await get_ride.click()
                    await page.wait_for_timeout(2000)
                dest_input = page.get_by_role("searchbox").last
            await dest_input.fill(home_address)
            await page.wait_for_timeout(2000)

            # --- Step 3: Pick first autocomplete suggestion ---
            suggestion = page.locator("[data-testid='search-result']").first
            if await suggestion.is_visible(timeout=3000):
                await suggestion.click()
            else:
                await dest_input.press("Enter")
            await page.wait_for_timeout(2000)

            # --- Step 4: Schedule (not ride now) ---
            schedule_btn = page.get_by_text("Schedule", exact=False)
            if await schedule_btn.is_visible(timeout=3000):
                await schedule_btn.click()
                await page.wait_for_timeout(1000)

                time_input = page.locator("input[type='time']").first
                if await time_input.is_visible(timeout=2000):
                    await time_input.fill(pickup_time.strftime("%H:%M"))
                    await page.wait_for_timeout(500)

                set_btn = page.get_by_role(
                    "button", name=re.compile(r"^(set|done|confirm)$", re.I)
                )
                if await set_btn.is_visible(timeout=2000):
                    await set_btn.click()
                await page.wait_for_timeout(1000)

            # --- Step 5: Confirm ride ---
            confirm_btn = page.get_by_role(
                "button", name=re.compile(r"confirm|request uber|book", re.I)
            )
            if await confirm_btn.is_visible(timeout=5000):
                await confirm_btn.click()
                await page.wait_for_timeout(3000)
                print(f"[RIDE] Booking submitted for {time_label}")
                return True

            print("[RIDE] Confirm button not found — booking did not complete")
            return False

        except PWTimeout as e:
            print(f"[RIDE] Timeout: {e}")
            return False
        except Exception as e:
            print(f"[RIDE] Error: {e}")
            return False
        finally:
            await browser.close()


class UberSkill:
    def request_ride(self, pickup_time: datetime, lat: float, lon: float) -> bool:
        # lat/lon kept for interface compatibility; geolocation is injected via Playwright
        return asyncio.run(_book_ride_async(pickup_time, STATE_PATH))
