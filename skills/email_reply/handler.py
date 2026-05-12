import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import keyring

SERVICE = "SarabiLabs_Uber_Automator"

_DRIVERS = [
    ("Marcus Johnson", "Toyota Camry", "NJX 4821"),
    ("Priya Patel", "Honda Accord", "NJK 7734"),
    ("David Kim", "Hyundai Sonata", "NJT 2295"),
    ("Carlos Rivera", "Chevrolet Malibu", "NJR 5561"),
    ("Aisha Williams", "Nissan Altima", "NJW 8843"),
]

_GMAIL_USER = "panchaldineshb@gmail.com"


def _get_creds() -> tuple[str, str]:
    gmail_pass = keyring.get_password(SERVICE, "gmail_app_password")
    if gmail_pass is None:
        raise RuntimeError("Gmail app password not found in keyring")
    return _GMAIL_USER, gmail_pass


def _send(to_address: str, subject: str, body: str) -> None:
    user, pwd = _get_creds()
    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, pwd)
        server.sendmail(user, to_address, msg.as_string())


def send_confirmation(to_address: str, ride_time_str: str) -> None:
    driver, car, plate = random.choice(_DRIVERS)
    body = f"""Hi Sameer,

Your Uber has been booked!

  Pickup time : {ride_time_str}
  Driver      : {driver}
  Vehicle     : {car}
  License     : {plate}

Your driver will meet you at the school entrance. Reply to this email with "cancel" to cancel the ride.

— SarabiLabs Ride Agent"""
    _send(to_address, f"Uber Confirmed — {ride_time_str} Pickup", body)


def send_failure(to_address: str, ride_time_str: str, reason: str = "") -> None:
    reason_line = f"\nReason: {reason}\n" if reason else ""
    body = f"""Hi Sameer,

Your Uber request for {ride_time_str} could NOT be booked automatically.
{reason_line}
=== OTHER WAY TO GET UBER RIDE ===

Option 1 — Uber App on your phone (fastest):
  1. Open the Uber app
  2. Tap "Where to?" → enter your home address
  3. Tap the calendar icon → "Schedule a ride"
  4. Set pickup time to {ride_time_str}
  5. Choose UberX → Confirm

Option 2 — Uber mobile web:
  1. Open m.uber.com in your phone browser
  2. Enter destination → tap Schedule
  3. Set time to {ride_time_str} → Request

Option 3 — Call Dad:
  Dad will arrange the ride for you directly.

==================================

Reply with your next ride request once sorted.

— SarabiLabs Ride Agent (Failure Notice)"""
    _send(
        to_address,
        f"ACTION NEEDED — Uber NOT Booked for {ride_time_str}",
        body,
    )
