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


def send_confirmation(to_address: str, ride_time_str: str):
    driver, car, plate = random.choice(_DRIVERS)
    gmail_user = "panchaldineshb@gmail.com"
    gmail_pass = keyring.get_password(SERVICE, "gmail_app_password")

    body = f"""Hi Sameer,

Your Uber has been booked!

  Pickup time : {ride_time_str}
  Driver      : {driver}
  Vehicle     : {car}
  License     : {plate}

Your driver will meet you at the school entrance. Reply to this email with "cancel" to cancel the ride.

— SarabiLabs Ride Agent"""

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_address
    msg["Subject"] = f"Uber Confirmed — {ride_time_str} Pickup"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_address, msg.as_string())
