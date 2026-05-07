import keyring
from google.oauth2.credentials import Credentials

class SarabiAuth:
    SERVICE = "SarabiLabs_Uber_Automator"

    @classmethod
    def get_creds(cls):
        # Fetch from Keychain
        r_token = keyring.get_password(cls.SERVICE, "google_refresh_token")
        c_id = keyring.get_password(cls.SERVICE, "google_client_id")
        c_secret = keyring.get_password(cls.SERVICE, "google_client_secret")

        if not all([r_token, c_id, c_secret]):
            raise ValueError("Missing Google OAuth credentials in Keychain.")

        return Credentials(
            token=None,
            refresh_token=r_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=c_id,
            client_secret=c_secret
        )