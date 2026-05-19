## Purpose
Verify Gmail IMAP is reachable before entering the poll loop.
Prevents the agent from spinning on connection errors.

## Inputs
None.

## Outputs
`bool` — True if IMAP login succeeds, False otherwise.

## Dependencies
- `imaplib` (stdlib)
- `keyring` — reads `gmail_app_password` from `SarabiLabs_Uber_Automator`
- `core.settings` — reads `GMAIL_USER`

## Public API
```python
from skills.gmail_precheck.handler import check_gmail_available

available: bool = check_gmail_available()
```
