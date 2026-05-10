import os
import keyring
from twilio.rest import Client

class sms_notifier:
    SERVICE_NAME = "SarabiLabs_Uber_Automator"

    @classmethod
    def send_confirmation(cls, to_number, message_body):
        # Retrieve credentials from Keychain
        account_sid = keyring.get_password(cls.SERVICE_NAME, "twilio_sid")
        auth_token = keyring.get_password(cls.SERVICE_NAME, "twilio_token")
        from_number = keyring.get_password(cls.SERVICE_NAME, "twilio_phone")

        if not all([account_sid, auth_token, from_number]):
            raise RuntimeError("Twilio credentials missing in Keychain. Run 'make seed-secrets'.")

        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        return message.sid