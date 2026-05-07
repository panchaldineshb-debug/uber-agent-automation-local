from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state="auth/uber_state.json"
    )

    page = context.new_page()

    page.goto(
        "https://www.uber.com/",
        wait_until="networkidle"
    )

    print("Uber session restored successfully")

    input("\nPress ENTER to close browser...\n")

    browser.close()