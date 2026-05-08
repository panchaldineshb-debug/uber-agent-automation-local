from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import requests
import os

AUTH_FILE = Path("auth/uber_state.json")
OLLLAMA_API_BASE = os.getenv("OLLLAMA_API_BASE", "http://localhost:11434")

AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)

    context = browser.new_context()

    page = context.new_page()

    page.goto("https://auth.uber.com/login/", wait_until="networkidle")

    print("\nLogin manually in browser...")
    print("Complete MFA / OTP if required.\n")

    # Wait until user lands on Uber homepage/dashboard
    page.wait_for_url("**uber.com/**", timeout=300000)

    # Extra stabilization
    time.sleep(5)

    context.storage_state(path=str(AUTH_FILE))

    print(f"\nSaved auth state -> {AUTH_FILE}")

    # Send a POST request to the Ollama API
    response = requests.post(f"{OLLLAMA_API_BASE}/some_endpoint", json={"key": "value"})
    if response.status_code == 200:
        print("POST request to Ollama API successful")
    else:
        print(f"POST request to Ollama API failed with status code {response.status_code}")

    browser.close()
