import requests as http
from google.auth.transport.requests import Request
from skills.gmail_auth.handler import SarabiAuth

GMAIL_PROFILE_URL = "https://gmail.googleapis.com/gmail/v1/users/me/profile"


def check_gmail_available() -> bool:
    try:
        creds = SarabiAuth.get_creds()
        creds.refresh(Request())
        resp = http.get(
            GMAIL_PROFILE_URL,
            headers={"Authorization": f"Bearer {creds.token}"},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"[WARN] Gmail pre-check failed: {e}")
        return False
