"""
Fetch Uber ride ETAs and prices for a given pickup/dropoff without booking.
Uses the saved browser session when available; falls back to anonymous.

Usage:
    make uber-eta
    uv run python scripts/uber_eta.py
    uv run python scripts/uber_eta.py "855 Grove Ave, Edison, NJ" "39 Henry St, Edison, NJ"
"""
import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

STATE_PATH = "config/uber_state.json"
HEADLESS = os.environ.get("UBER_HEADLESS", "true").lower() != "false"

DEFAULT_PICKUP = "855 Grove Ave, Edison, NJ 08820"
DEFAULT_DROPOFF = os.environ.get("UBER_DROPOFF", "")


async def get_uber_eta(pickup_address: str, dropoff_address: str) -> list[dict]:
    """
    Automates m.uber.com/go/home to fetch ride availability and ETAs.
    Note: To book a ride, user authentication would be required.
    """
    use_session = os.path.exists(STATE_PATH)
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        ctx_kwargs = {"storage_state": STATE_PATH} if use_session else {}
        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()

        try:
            await page.goto("https://m.uber.com/looking", timeout=30000)
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_timeout(4000)
            print(f"[ETA] url: {page.url}")

            # Dismiss banners
            for label in ("Got it", "Opt out"):
                btn = page.get_by_text(label, exact=True)
                try:
                    if await btn.is_visible(timeout=1000):
                        await btn.click()
                        await page.wait_for_timeout(300)
                except Exception:
                    pass

            # Fill pickup (first combobox)
            inputs = page.locator('input[role="combobox"]')
            count = await inputs.count()
            print(f"[ETA] combobox inputs found: {count}  url: {page.url}")

            if count < 1:
                print("[ETA] No combobox inputs found — cannot proceed.")
                return []

            async def fill_and_select(inp, address: str, label: str):
                await inp.wait_for(state="visible", timeout=8000)
                await inp.fill(address)
                await page.wait_for_timeout(2000)
                # Prefer li[role='option'] — that's what Uber renders
                opts = page.locator("li[role='option']")
                if await opts.count() > 0:
                    await opts.first.click()
                else:
                    await inp.press("Enter")
                await page.wait_for_timeout(1500)
                print(f"[ETA] {label} selected, url: {page.url}")

            pickup_input = inputs.nth(0)
            await fill_and_select(pickup_input, pickup_address, "pickup")

            inputs = page.locator('input[role="combobox"]')
            dropoff_input = inputs.last
            await fill_and_select(dropoff_input, dropoff_address, "dropoff")

            # Click Search to load ride options
            search_btn = page.get_by_role("button", name="Search")
            if await search_btn.is_visible(timeout=3000):
                await search_btn.click()
                print("[ETA] Clicked Search")
            await page.wait_for_timeout(5000)
            print(f"[ETA] After search, url: {page.url}")

            await page.screenshot(path="logs/eta_state.png")
            print("[ETA] Screenshot: logs/eta_state.png")

            # Scrape ride options
            ride_cards = page.locator("[data-testid='product-card'], [data-testid='vehicle-view-product-card']")
            card_count = await ride_cards.count()
            print(f"[ETA] ride option cards found: {card_count}")

            if card_count == 0:
                # Fallback: any visible text blocks with price/time patterns
                content = await page.evaluate("""() => {
                    const els = [...document.querySelectorAll('li, [role="listitem"], [class*="product"], [class*="vehicle"]')];
                    return els.map(e => e.innerText.trim()).filter(t => t && /\\$|min|UberX|Comfort|Black/i.test(t)).slice(0, 20);
                }""")
                print("[ETA] Fallback text:", content)
                results = [{"raw": t} for t in content] if content else [{"raw": "no results — check logs/eta_state.png"}]
            else:
                for i in range(card_count):
                    card = ride_cards.nth(i)
                    text = await card.inner_text()
                    results.append({"option": i + 1, "text": text.strip()})

        except Exception as e:
            print(f"[ETA] Error: {e}")
            try:
                await page.screenshot(path="logs/eta_error.png")
                print("[ETA] Screenshot saved: logs/eta_error.png")
            except Exception:
                pass
        finally:
            await browser.close()

    return results


if __name__ == "__main__":
    pickup = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PICKUP
    dropoff = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DROPOFF

    if not dropoff:
        try:
            import keyring
            dropoff = keyring.get_password("SarabiLabs_Uber_Automator", "home_address") or ""
        except Exception:
            pass

    if not dropoff:
        print("[ETA] No dropoff address. Set UBER_DROPOFF env var or pass as second arg.")
        sys.exit(1)

    print(f"[ETA] pickup:  {pickup}")
    print(f"[ETA] dropoff: {dropoff}")

    rides = asyncio.run(get_uber_eta(pickup, dropoff))
    if rides:
        print("\n[ETA] Results:")
        print(json.dumps(rides, indent=2))
    else:
        print("[ETA] No results returned.")
