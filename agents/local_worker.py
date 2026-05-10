import imaplib
import email
import time
import asyncio
from typing import Optional

# Core SarabiLabs Imports
from core import settings, logger, sarabilabs_monitor
from scripts.check_session import is_session_valid

# Skill Imports
from skills.email_parser.handler import EmailParser
from skills.ride_request.handler import UberSkill
from skills.notifier.handler import sms_notifier
from skills.notifier.mac_alert import MacNotifier
from skills.email_reply.handler import send_confirmation
from skills.gmail_precheck.handler import check_gmail_available


class UberAgent:
    def __init__(self):
        logger.info(f"Booting SarabiLabs Agent on {settings.SERVICE_NAME}")

        self.uber = UberSkill()
        # Retrieve secrets once at startup to fail-fast
        self.gmail_pass = settings.get_keychain_secret()
        self.son_phone = settings.get_keychain_secret(key_name="son_phone")

    @sarabilabs_monitor
    def process_ride_intent(self, body: str):
        """Extracts intent and executes the ride request."""
        ride_time = EmailParser.extract_time(body)

        if not ride_time:
            raise RuntimeError(f"No valid ride time found in email body: {body[:100]!r}")

        ride_time_str = ride_time.strftime("%I:%M %p")

        # Coordinates for JP Stevens High School
        # Using settings or hardcoded constants for safety
        success = self.uber.request_ride(ride_time, 40.5482, -74.3444)

        if success:
            send_confirmation(settings.SON_EMAIL, ride_time_str)
            sms_notifier.send_confirmation(
                self.son_phone,
                f"Uber booked for {ride_time_str}. Check email for driver info.",
            )
            MacNotifier.notify_admin(
                "SarabiLabs", f"SUCCESS: Uber booked for {ride_time_str}"
            )
        else:
            # This raise will be caught by @sarabilabs_monitor and email you
            raise RuntimeError(f"Uber API failed to confirm ride for {ride_time_str}")

    def check_gmail_health(self):
        """Pre-check: verify Gmail OAuth token and API reachability."""
        if not check_gmail_available():
            msg = "Gmail API unavailable. Re-run 'make auth'."
            print(f"[WARN] {msg}")
            MacNotifier.notify_admin("SarabiLabs", msg)
            return False
        return True

    def check_uber_health(self):
        """Pre-flight check: warn if session is stale."""
        try:
            if not asyncio.run(is_session_valid()):
                msg = "Uber session expired. Run 'make auth' now."
                print(f"[WARN] {msg}")
                MacNotifier.notify_admin("SarabiLabs", msg)
        except Exception as e:
            print(f"[WARN] Health check skipped: {e}")

    @sarabilabs_monitor
    def poll_gmail(self):
        """Connects to Gmail and processes unread messages from Sameer."""
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.GMAIL_USER, self.gmail_pass)
        mail.select("inbox")

        # Search specifically for unread emails from the authorized sender
        status, messages = mail.search(None, f'(UNSEEN FROM "{settings.SON_EMAIL}")')

        for num in messages[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            self.process_ride_intent(body)

        mail.close()
        mail.logout()


def run_agent():
    print(f"--- SarabiLabs Agent Starting [{settings.SERVICE_NAME}] ---")
    agent = UberAgent()

    while True:
        # 1. Health Checks
        agent.check_uber_health()
        if not agent.check_gmail_health():
            time.sleep(300)
            continue

        # 2. Poll and Process
        agent.poll_gmail()

        # 3. Wait (Default 5 mins)
        time.sleep(300)


if __name__ == "__main__":
    run_agent()
