import imaplib
import email
import time
from skills.email_parser.handler import EmailParser
from skills.ride_request.handler import UberSkill
from skills.notifier.handler import sms_notifier
from skills.notifier.mac_alert import MacNotifier
from skills.email_reply.handler import send_confirmation

import keyring

SERVICE = "SarabiLabs_Uber_Automator"
GMAIL_USER = "panchaldineshb@gmail.com"
GMAIL_PASS = keyring.get_password(SERVICE, "gmail_app_password")
SON_EMAIL = "3016203@edison.k12.nj.us"


def process_ride_intent(body):
    SON_PHONE = keyring.get_password(SERVICE, "son_phone")

    if not SON_PHONE:
        print("Error: SON_PHONE not found in Keychain. Run 'make seed-secrets'.")
        return

    ride_time = EmailParser.extract_time(body)
    if ride_time:
        ride_time_str = ride_time.strftime("%I:%M %p")

        uber = UberSkill()
        uber.request_ride(ride_time, 40.518, -74.412)

        send_confirmation(SON_EMAIL, ride_time_str)
        sms_notifier.send_confirmation(
            SON_PHONE,
            f"Uber booked for {ride_time_str}. Check your email for driver details.",
        )
        MacNotifier.notify_admin("SarabiLabs", f"Uber booked for {ride_time_str}")


def poll_and_process():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")

        # Search for unread emails from your son
        status, messages = mail.search(None, f'(UNSEEN FROM "{SON_EMAIL}")')

        for num in messages[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1].decode("utf-8")
            msg = email.message_from_string(raw_email)

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            process_ride_intent(body)

        mail.close()
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("SarabiLabs Local Ride Agent Active. Polling every 5 minutes...")
    while True:
        poll_and_process()
        time.sleep(300)  # 5 Minute interval
