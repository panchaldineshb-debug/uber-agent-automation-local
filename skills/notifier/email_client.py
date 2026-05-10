import smtplib
import keyring
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.settings import settings

SERVICE = "SarabiLabs_Uber_Automator"
ADMIN_EMAIL = "panchaldineshb@gmail.com"


def _send_email(to_address: str, subject: str, body: str):
    gmail_user = settings.GMAIL_USER
    gmail_pass = keyring.get_password(SERVICE, "gmail_app_password")
    if gmail_pass is None:
        raise RuntimeError("Keychain entry 'gmail_app_password' not found.")

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_pass)
        server.sendmail(gmail_user, to_address, msg.as_string())


def send_failure_email(error_msg: str, func_name: str):
    sameer_body = (
        f"Hi Sameer,\n\nThe Uber ride automation failed.\n"
        f"ACTION: Call Dad or use your own app immediately.\n\n"
        f"Error Ref: {func_name}"
    )
    admin_body = (
        f"SARABILABS ALERT\n"
        f"Function '{func_name}' crashed on M4 Mini.\n\n"
        f"ERROR DETAILS:\n{error_msg}\n\n"
        f"Check logs in your 'logs/' folder for tracebacks."
    )

    _send_email(settings.SON_EMAIL, "Uber Automation Failed — Action Required", sameer_body)
    _send_email(ADMIN_EMAIL, f"[SarabiLabs] Failure in {func_name}", admin_body)
