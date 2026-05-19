## Purpose
Send confirmation or failure emails via SMTP to Sameer after a ride-booking attempt.

## Inputs
- `to`: recipient email address
- `ride_time_str`: human-readable time string e.g. "2:35 PM"
- `reason` (failure only): why booking failed

## Outputs
None — side-effect only (email sent via Gmail SMTP).

## Dependencies
- `smtplib`, `email.mime` (stdlib)
- `keyring` — reads `gmail_app_password` from `SarabiLabs_Uber_Automator`

## Public API
```python
from skills.email_reply.handler import send_confirmation, send_failure

send_confirmation(to: str, ride_time_str: str) -> None
send_failure(to: str, ride_time_str: str, reason: str) -> None
```
