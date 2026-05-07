import asyncio
import os
from playwright.async_api import async_playwright


async def is_session_valid(state_path="config/uber_state.json"):
    if not os.path.exists(state_path):
        print("[CHECK] Session file missing.")
        return False

    async with async_playwright() as p:
        # Launch headless to be fast and invisible
        browser = await p.chromium.launch(headless=True)
        # Load the saved state
        context = await browser.new_context(storage_state=state_path)
        page = await context.new_page()

        try:
            # Go to the 'Looking' page (the main logged-in dashboard)
            await page.goto("https://m.uber.com/looking", timeout=15000)

            # Wait a moment for redirects
            await page.wait_for_load_state("networkidle")

            # Check the URL: If it contains 'login' or 'auth', the session is dead
            current_url = page.url
            if "auth.uber.com" in current_url or "login" in current_url:
                print("[CHECK] Session EXPIRED. Re-authentication required.")
                return False

            print("[CHECK] Session is VALID. Ready to book rides.")
            return True

        except Exception as e:
            print(f"[CHECK] Error during verification: {e}")
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    valid = asyncio.run(is_session_valid())
    exit(0 if valid else 1)
