import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

STATE_PATH = "config/uber_state.json"
MAX_SESSION_AGE_DAYS = 7


def _session_file_fresh(state_path: str) -> bool:
    try:
        age_days = (datetime.now().timestamp() - os.stat(state_path).st_mtime) / 86400
        return age_days < MAX_SESSION_AGE_DAYS
    except OSError:
        return False


async def is_session_valid(state_path: str = STATE_PATH) -> bool:
    if not os.path.exists(state_path):
        print("[CHECK] Session file missing — run 'make uber-login'.")
        return False

    if not _session_file_fresh(state_path):
        print(f"[CHECK] Session older than {MAX_SESSION_AGE_DAYS} days — run 'make uber-login'.")
        return False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=state_path)
        page = await context.new_page()

        try:
            await page.goto("https://m.uber.com/looking", timeout=30000)
            # Uber's SPA never reaches networkidle — wait for DOM then settle
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_timeout(4000)

            url = page.url
            print("[CHECK] url:", url)

            # Hard expired: redirected to auth
            if "auth.uber.com" in url or "/login" in url:
                print("[CHECK] Session EXPIRED — redirected to login.")
                return False

            # Uber's React app uses non-link elements for auth prompts — match by text
            try:
                if await page.get_by_text("Log in", exact=True).is_visible(timeout=2000):
                    print("[CHECK] Session EXPIRED — 'Log in' prompt visible.")
                    return False
            except Exception:
                pass

            # Positive check: authenticated users have an account chevron in the nav
            # SVG <title> elements are metadata — use count(), not is_visible()
            try:
                chevron_count = await page.locator('title:text("Chevron down small")').count()
                if chevron_count == 0:
                    print("[CHECK] Session EXPIRED — account chevron not found.")
                    return False
            except Exception:
                print("[CHECK] Session EXPIRED — account chevron lookup failed.")
                return False

            print("[CHECK] Session VALID.")
            return True

        except Exception as e:
            print(f"[CHECK] Error during session check: {e}")
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    valid = asyncio.run(is_session_valid())
    exit(0 if valid else 1)
