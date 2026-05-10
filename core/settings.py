import os
from pathlib import Path
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 1. Resolve Path and Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# 2. Fetch and Validate Presence (Type Guarding)
# We pull the values into local variables first
_gmail_user = os.getenv("GMAIL_USER")
_son_email = os.getenv("SON_EMAIL")

# Brutal Logic: If these are None, the app is fundamentally broken.
# Raising an error here satisfies Pylance because it knows the code
# won't reach the 'Settings' call if the values are None.
if _gmail_user is None or _son_email is None:
    missing = []
    if not _gmail_user:
        missing.append("GMAIL_USER")
    if not _son_email:
        missing.append("SON_EMAIL")
    raise EnvironmentError(
        f"CRITICAL: Missing required .env variables: {', '.join(missing)}"
    )


class Settings(BaseSettings):
    GMAIL_USER: EmailStr
    SON_EMAIL: EmailStr
    SERVICE_NAME: str = "SarabiLabs_Uber_Automator"

    # Paths derived from BASE_DIR
    LOG_DIR: Path = BASE_DIR / "logs"
    UBER_STATE_FILE: Path = BASE_DIR / "config" / "uber_state.json"

    model_config = SettingsConfigDict(extra="ignore")

    def get_keychain_secret(self, key_name: str = "gmail_app_password") -> str:
        import keyring
        secret = keyring.get_password(self.SERVICE_NAME, key_name)
        if secret is None:
            raise RuntimeError(f"Keychain entry '{self.SERVICE_NAME}/{key_name}' not found.")
        return secret


# 3. Explicit Initialization
# Pylance now sees that _gmail_user and _son_email MUST be strings
settings = Settings(GMAIL_USER=_gmail_user, SON_EMAIL=_son_email)
