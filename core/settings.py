import os
import subprocess
from pathlib import Path
from pydantic import Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Constants from .env
    SERVICE_NAME: str = Field(default="SarabiLabs_Uber_Automator")
    GMAIL_USER: EmailStr
    SON_EMAIL: EmailStr
    
    # Paths
    UBER_STATE_FILE: Path = BASE_DIR / "config" / "uber_state.json"
    LOG_DIR: Path = BASE_DIR / "logs"

    # Pydantic will automatically look for a .env file
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore"
    )

    def get_keychain_secret(self) -> str:
        """
        Brutal DevOps Logic: Fetch the secret directly from macOS Keychain.
        This ensures 100% local privacy.
        """
        try:
            command = f"security find-generic-password -w -s {self.SERVICE_NAME}"
            secret = subprocess.check_output(command, shell=True).decode("utf-8").strip()
            return secret
        except subprocess.CalledProcessError:
            # This triggers your @sarabilabs_monitor decorator if used in agents
            raise RuntimeError(f"Secret for {self.SERVICE_NAME} not found in Keychain.")

# Global instance to be imported elsewhere
settings = Settings()