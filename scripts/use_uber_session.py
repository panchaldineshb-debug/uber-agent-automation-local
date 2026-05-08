from playwright.sync_api import sync_playwright
import requests
import os

OLLLAMA_API_BASE = os.getenv("OLLLAMA_API_BASE", "http://localhost:11434")

def main():
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

        # Send a POST request to the Ollama API
        response = requests.post(f"{OLLLAMA_API_BASE}/some_endpoint", json={"key": "value"})
        if response.status_code == 200:
            print("POST request to Ollama API successful")
        else:
            print(f"POST request to Ollama API failed with status code {response.status_code}")

        input("\nPress ENTER to close browser...\n")

        browser.close()

if __name__ == "__main__":
    main()
