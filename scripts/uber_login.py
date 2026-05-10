from playwright.sync_api import sync_playwright
from pathlib import Path
import time

AUTH_FILE = Path("config/uber_state.json")


def main():
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://auth.uber.com/login/", wait_until="load")

        print("\nLogin manually in the browser window.")
        print("Complete MFA / OTP if required.\n")

        page.wait_for_url("**uber.com/**", timeout=300000)
        time.sleep(5)

        context.storage_state(path=str(AUTH_FILE))
        print(f"\nSession saved -> {AUTH_FILE}")

        browser.close()


if __name__ == "__main__":
    main()
