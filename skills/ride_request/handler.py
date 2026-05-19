import re
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
import keyring
from core.geocoder import get_coordinates, validate_edison_nj

SERVICE_NAME = "SarabiLabs_Uber_Automator"
STATE_PATH = "config/uber_state.json"
SCHOOL_ADDRESS = "855 Grove Ave, Edison, NJ 08820"

HEADLESS = os.environ.get("UBER_HEADLESS", "true").lower() != "false"
DRY_RUN = os.environ.get("UBER_DRY_RUN", "false").lower() == "true"


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

    if not validate_edison_nj(SCHOOL_ADDRESS):
        print(f"[RIDE] Pickup outside Edison NJ — aborting: {SCHOOL_ADDRESS!r}")
        return False
    if not validate_edison_nj(home_address):
        print(f"[RIDE] Dropoff outside Edison NJ — aborting: {home_address!r}")
        return False

    pickup_lat, pickup_lon = get_coordinates(SCHOOL_ADDRESS)
    print(f"[RIDE] Pickup coords: {pickup_lat:.4f}, {pickup_lon:.4f}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            storage_state=state_path,
            geolocation={"latitude": pickup_lat, "longitude": pickup_lon},
            permissions=["geolocation"],
        )
        page = await context.new_page()

        try:
            await page.goto("https://m.uber.com/looking", timeout=30000)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_timeout(4000)
            print(f"[RIDE] Page URL after load: {page.url}")

            # Dismiss any cookie/promo banners
            for banner_text in ("Got it", "Opt out"):
                btn = page.get_by_text(banner_text, exact=True)
                if await btn.is_visible(timeout=1000):
                    await btn.click()
                    await page.wait_for_timeout(500)

            # --- Step 1: Fill destination — Uber uses role="combobox" inputs ---
            # Two comboboxes: [0]=pickup, [1]=destination
            dest_input = page.locator('input[role="combobox"]').last
            await dest_input.wait_for(state="visible", timeout=8000)
            await dest_input.fill(home_address)
            await page.wait_for_timeout(2000)

            # --- Step 2: Pick first autocomplete suggestion ---
            suggestion = page.locator("[data-testid='search-result']").first
            if await suggestion.is_visible(timeout=3000):
                await suggestion.click()
            else:
                await dest_input.press("Enter")
            await page.wait_for_timeout(2000)

            # --- Step 3: Schedule (not ride now) ---
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

            # --- Step 4: Confirm ride ---
            confirm_btn = page.get_by_role(
                "button", name=re.compile(r"confirm|request uber|book", re.I)
            )
            if await confirm_btn.is_visible(timeout=5000):
                if DRY_RUN:
                    print(f"[RIDE] DRY RUN — confirm button found, skipping click for {time_label}")
                    return True
                await confirm_btn.click()
                await page.wait_for_timeout(3000)
                print(f"[RIDE] Booking submitted for {time_label}")
                return True

            print("[RIDE] Confirm button not found — booking did not complete")
            return False

        except PWTimeout as e:
            try:
                await page.screenshot(path="logs/ride_timeout.png")
            except Exception:
                pass
            print(f"[RIDE] Timeout: {e}")
            return False
        except Exception as e:
            try:
                await page.screenshot(path="logs/ride_error.png")
            except Exception:
                pass
            print(f"[RIDE] Error: {e}")
            return False
        finally:
            await browser.close()


class UberSkill:
    def request_ride(self, pickup_time: datetime, lat: float, lon: float) -> bool:
        # lat/lon kept for interface compatibility; coords now derived from SCHOOL_ADDRESS
        return asyncio.run(_book_ride_async(pickup_time, STATE_PATH))
