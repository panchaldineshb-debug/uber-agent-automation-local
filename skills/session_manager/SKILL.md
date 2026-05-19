## Purpose
Check Uber browser session validity. Does NOT refresh or login — manual `make uber-login` required.

## Inputs
None.

## Outputs
- `is_valid() -> bool` — True if Playwright session check passes
- `refresh_needed() -> bool` — True if file missing or older than 7 days (no Playwright)

## Dependencies
- `playwright` (via scripts/check_session.py — only for `is_valid()`)
- `config/uber_state.json` — session state file

## Public API
```python
from skills.session_manager.handler import SessionManager

sm = SessionManager()
sm.is_valid()         # -> bool (Playwright check)
sm.refresh_needed()   # -> bool (file-level check, fast)
sm.state_path()       # -> "config/uber_state.json"
```

## Notes
`refresh_needed()` is safe to call in the poll loop — no browser launched.
`is_valid()` launches Chromium — use sparingly.
