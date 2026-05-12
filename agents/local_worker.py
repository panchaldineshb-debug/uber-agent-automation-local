import imaplib
import email
import time
import asyncio
from typing import Optional

from core import settings, logger, sarabilabs_monitor
from scripts.check_session import is_session_valid

from skills.email_parser.handler import EmailParser
from skills.ride_request.handler import UberSkill
from skills.notifier.handler import sms_notifier
from skills.notifier.mac_alert import MacNotifier
from skills.email_reply.handler import send_confirmation, send_failure
from skills.gmail_precheck.handler import check_gmail_available


class UberAgent:
    def __init__(self):
        logger.info(f"Booting SarabiLabs Agent on {settings.SERVICE_NAME}")
        self.uber = UberSkill()
        self.gmail_pass = settings.get_keychain_secret()
        self.son_phone = settings.get_keychain_secret(key_name="son_phone")

    def process_ride_intent(self, body: str) -> None:
        ride_time = EmailParser.extract_time(body)

        if not ride_time:
            msg = f"No valid ride time in email: {body[:80]!r}"
            send_failure(settings.SON_EMAIL, "unknown time", reason=msg)
            raise RuntimeError(msg)

        ride_time_str = ride_time.strftime("%-I:%M %p")

        try:
            success = self.uber.request_ride(ride_time, 40.5482, -74.3444)
        except Exception as e:
            reason = str(e)
            send_failure(settings.SON_EMAIL, ride_time_str, reason=reason)
            sms_notifier.send_confirmation(
                self.son_phone,
                f"Uber booking FAILED for {ride_time_str}. Check email for manual steps.",
            )
            MacNotifier.notify_admin("SarabiLabs", f"FAILED: Uber booking error — {reason}")
            raise

        if success:
            send_confirmation(settings.SON_EMAIL, ride_time_str)
            sms_notifier.send_confirmation(
                self.son_phone,
                f"Uber booked for {ride_time_str}. Check email for driver info.",
            )
            MacNotifier.notify_admin("SarabiLabs", f"SUCCESS: Uber booked for {ride_time_str}")
        else:
            reason = "Playwright flow did not reach confirmation step"
            send_failure(settings.SON_EMAIL, ride_time_str, reason=reason)
            sms_notifier.send_confirmation(
                self.son_phone,
                f"Uber booking FAILED for {ride_time_str}. Check email for manual steps.",
            )
            MacNotifier.notify_admin("SarabiLabs", f"FAILED: {reason}")
            raise RuntimeError(f"Uber booking failed for {ride_time_str}")

    def check_gmail_health(self) -> bool:
        if not check_gmail_available():
            msg = "Gmail API unavailable. Re-run 'make auth'."
            print(f"[WARN] {msg}")
            MacNotifier.notify_admin("SarabiLabs", msg)
            return False
        return True

    def check_uber_health(self) -> bool:
        try:
            valid = asyncio.run(is_session_valid())
        except Exception as e:
            print(f"[WARN] Session check error: {e}")
            return True  # Don't block on infrastructure error; try anyway

        if not valid:
            msg = "Uber session expired. Run 'make auth' now."
            print(f"[WARN] {msg}")
            MacNotifier.notify_admin("SarabiLabs", msg)
        return valid

    @sarabilabs_monitor
    def poll_gmail(self) -> None:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.GMAIL_USER, self.gmail_pass)
        mail.select("inbox")

        status, messages = mail.search(None, f'(UNSEEN FROM "{settings.SON_EMAIL}")')

        for num in messages[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            if not data or not isinstance(data[0], tuple):
                continue
            raw_bytes: bytes = data[0][1]  # type: ignore[assignment]
            msg = email.message_from_bytes(raw_bytes)

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        body = payload.decode() if isinstance(payload, bytes) else str(payload)  # type: ignore[union-attr]
                        break
            else:
                payload = msg.get_payload(decode=True)
                body = payload.decode() if isinstance(payload, bytes) else str(payload)  # type: ignore[union-attr]

            try:
                self.process_ride_intent(body)
            except Exception as e:
                # Already notified Sameer; log and continue to next email
                print(f"[ERROR] process_ride_intent: {e}")

        mail.close()
        mail.logout()


def run_agent():
    print(f"--- SarabiLabs Agent Starting [{settings.SERVICE_NAME}] ---")
    agent = UberAgent()

    while True:
        # 1. Gmail health — skip poll if OAuth is broken
        if not agent.check_gmail_health():
            time.sleep(300)
            continue

        # 2. Uber session — skip poll if session is dead (Sameer can't get a ride anyway)
        if not agent.check_uber_health():
            time.sleep(300)
            continue

        # 3. Poll and process
        agent.poll_gmail()

        # 4. Wait 5 minutes
        time.sleep(300)


if __name__ == "__main__":
    run_agent()
