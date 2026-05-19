## Purpose
Send SMS via Twilio and macOS system notifications after ride booking.

## Inputs
- `phone`: E.164 phone number e.g. "+17325551234"
- `message`: notification body string

## Outputs
None — side-effect only.

## Dependencies
- `twilio` — reads `twilio_sid`, `twilio_token`, `twilio_phone` from keychain
- `keyring`
- `subprocess` — osascript for macOS alert (mac_alert.py)

## Public API
```python
from skills.notifier.handler import sms_notifier
from skills.notifier.mac_alert import MacNotifier

sms_notifier.send_confirmation(phone: str, message: str) -> None
MacNotifier.notify(title: str, body: str) -> None
```
