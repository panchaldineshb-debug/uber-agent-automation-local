import keyring
from google_auth_oauthlib.flow import InstalledAppFlow

SERVICE = "SarabiLabs_Uber_Automator"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def bootstrap_auth():
    # 1. Run the browser flow (Requires client_secrets.json in root)
    flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # 2. Extract and store the critical tokens
    keyring.set_password(SERVICE, "google_refresh_token", creds.refresh_token)
    keyring.set_password(SERVICE, "google_client_id", creds.client_id)
    keyring.set_password(SERVICE, "google_client_secret", creds.client_secret)
    
    print("✅ Success! Tokens migrated to macOS Keychain.")
    print("🗑️  You can now safely delete 'client_secrets.json'.")

if __name__ == "__main__":
    bootstrap_auth()